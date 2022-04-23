import json
import uuid
import requests


class Kard:
	def __init__(self):
		self.secrets = KardLocalSecrets()

		self.sl = requests.Session()
		self.s = requests.Session()

		self.api_host = "https://api.kard.eu/graphql"
		
		self.sl.headers = {
			'content-type': "application/json",
			'host': "api.kard.eu",
			'connection': "Keep-Alive",
			'accept-encoding': "gzip",
			'user-agent': self.secrets.user_agent,
			'vendoridentifier': self.secrets.vendor_identifier,
			'accept-language': "en"
		}
		self.s.headers = {
			"content-type": "application/json",
			"connection": "Keep-Alive",
			"accept-encoding": "gzip",
			'user-agent': self.secrets.user_agent,
			'vendoridentifier': self.secrets.vendor_identifier,
			"authorization": f"Bearer {self.secrets.access_token}",
			"accept-language": "en"
		}

	def init(self):
		self.login = KardLogin()
		self.account = KardAccount()
		self.cards = KardCards()
		self.bank = KardBankAccount()
		self.subscription = KardSubscription()
		self.cashback = KardCashback()


class KardLocalSecrets(Kard):
	def __init__(self):
		with open('secrets.json', 'r') as f:
			secrets = json.load(f)

		self.vendor_identifier = secrets['vendorIdentifier']
		self.user_agent = secrets['userAgent']
		self.access_token = secrets['accessToken']
		self.refresh_token = secrets['refreshToken']
		self.pin_code = secrets['accountPin']
		self.phone_number = secrets['accountTel']

		self.update()

	def update(self, **kwargs):
		if self.vendor_identifier is None:
			self.vendor_identifier = f"ghrlt:{uuid.uuid4()}"


		new_secrets = {
			"vendorIdentifier": self.vendor_identifier,
			"userAgent": self.user_agent,
			"accessToken": kwargs.get('access_token') or self.access_token,
			"refreshToken": kwargs.get('refresh_token') or self.refresh_token,
			"accountPin": self.pin_code,
			"accountTel": self.phone_number
		}

		with open('secrets.json', 'w') as f:
			json.dump(new_secrets, f, indent=2)


class KardLogin(Kard):
	def __init__(self):
		super().__init__()

		if self.secrets.access_token:
			if self.is_still_logged_in():
				self.is_logged_in = True
				return

		self.init_login()

	def is_still_logged_in(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { id }",
			"variables":{},
			"extensions":{}
		}

		r = self.s.post(self.api_host, json=payload)
		if r.status_code == 401:
			return False
		return True

	def init_login(self):
		payload = {
			"query": "mutation androidInitSession($createUser: Boolean, $phoneNumber: PhoneNumber!, $platform: DevicePlatform, $vendorIdentifier: String!) { initSession(input: {createUser: $createUser, phoneNumber: $phoneNumber, platform: $platform, vendorIdentifier: $vendorIdentifier}) { challenge expiresAt errors { path message } }}",
			"variables": {
				"platform": "ANDROID", "createUser": True,
				"phoneNumber": self.secrets.phone_number,
				"vendorIdentifier": self.secrets.vendor_identifier
			},
			"extensions": {}
		}
		r = self.sl.post(self.api_host, json=payload).json()
		
		if r['data']['initSession'].get('challenge') == "OTP":
			otp = input("To authenticate, please type the OTP code received by SMS: ")

			payload = {
				"query": "mutation androidVerifyOTP($authenticationProvider: AuthenticationProviderInput, $code: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { verifyOtp(input: {authenticationProvider: $authenticationProvider, code: $code, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { challenge accessToken refreshToken errors { path message } }}",
				"variables": {
					"phoneNumber": self.secrets.phone_number,
					"vendorIdentifier": self.secrets.vendor_identifier,
					"code": otp
				},
				"extensions": {}
			}
			r = self.sl.post(self.api_host, json=payload).json()
			#good: {'data': {'verifyOtp': {'challenge': 'PASSCODE', 'accessToken': None, 'refreshToken': None, 'errors': []}}}
			#wrong: {'data': {'verifyOtp': {'challenge': None, 'accessToken': None, 'refreshToken': None, 'errors': [{'path': ['arguments', 'code'], 'message': 'That code didn’t work'}]}}}

			if not r['data']['verifyOtp']['challenge']:
				raise Exception(r['data']['verifyOtp']['errors'])


		payload = {
			"query": "mutation androidSignIn($authenticationProvider: AuthenticationProviderInput,$passcode: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { signIn(input: {authenticationProvider: $authenticationProvider,passcode: $passcode, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { accessToken refreshToken errors { path message } }}",
			"variables": {
				"passcode": self.secrets.pin_code,
				"phoneNumber": self.secrets.phone_number,
				"vendorIdentifier": self.secrets.vendor_identifier
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		#good:
		#wrong: {'data': {'signIn': {'accessToken': None, 'refreshToken': None, 'errors': [{'path': ['arguments', 'passcode'], 'message': 'Invalid passcode'}]}}}
		
		if not r['data']['signIn']['accessToken']:
			raise Exception(r['data']['signIn']['errors'])

		self.secrets.access_token = r['data']['signIn']['accessToken']
		self.secrets.refresh_token = r['data']['signIn']['refreshToken']

		self.s.headers['authorization'] = f"Bearer {self.secrets.access_token}"
		self.secrets.update(
			access_token=self.secrets.access_token,
			refresh_token=self.secrets.refresh_token
		)

		self.is_logged_in = True


class KardAccount(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked scheme ... on PhysicalCard { atm contactless swipe online design orderedAt }}\n\n"
				"fragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\n\n"
				"fragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name providerId price { value } }}\n\n"
				"fragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\n\n"
				"fragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined createdAt requestee { id firstName lastName avatar { url } } requester { id firstName lastName avatar { url } }}\n\n"
				"fragment Transaction_TransactionCashbackParts on Transaction { id title amount { value currency { symbol } } image { id url } processedAt category { name color image { url } } ... on CashbackTransaction { cashback { status brandLogo brandName sourceTransaction { id title image { id url } category { name color image { url } } amount { value currency { symbol } } } } }}\n\n"
				"fragment Me_MeParts on Me { id modirumId type intercomHashes { android } canFinishOnboarding profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } lockedTransactions } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt cashbackEnabled cashbackWallet { id balance { value currency { symbol isoCode } } amountEarned { value currency { symbol isoCode } } transactions(first: 10, order: CREATED, direction: DESC) { pageInfo { endCursor hasNextPage } nodes { ... Transaction_TransactionCashbackParts } } } invitedByOther topupIncentiveActivated hasUnreadActivityItems noPhoneNumber allowedToAddChild currentSpendings { monthlyPos { value } weeklyPos { value } weeklyAtm { value } monthlyAtm { value } } legalSpendingLimits { monthlyPos { value } weeklyPos { value } weeklyAtm { value } monthlyAtm { value } } transactionLimits { id amount { value currency { symbol } } recurrence transactionType } transactionAuthorizations { authorizationType isAuthorized }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']

	@property
	def id(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { id }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['id']

	@property
	def type(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { type }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['type']
	
	@property
	def firstname(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { firstName }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['firstName']
	
	@property
	def lastname(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { lastName } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['profile']['lastName']

	@property
	def username(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { username } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['profile']['username']

	@property
	def address(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { shippingAddress { fullAddress } } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['profile']['shippingAddress']['fullAddress']

	@property
	def email(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { email }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['email']

	@property
	def referralCode(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { referralCode }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['referralCode']

	@property
	def referralUrl(self):
		referralCode = self.referralCode
		return f"https://kard.eu?r={referralCode}"


class KardCards(Kard):
	def __init__(self):
		super().__init__()

	@property
	def all(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { cards { nodes { ... Card_CardParts }}}\n\n"
				"fragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['cards']['nodes']

	@property
	def physicals(self):
		cards = self.all
		return [card for card in cards if card['__typename'] == "PhysicalCard"]

	@property
	def virtuals(self):
		cards = self.all
		return [card for card in cards if card['__typename'] == "VirtualCard"]

	@property
	def virtuals_digits(self):
		cards = self.virtuals

		digits = []
		for card in cards:
			payload = {
				"query": "query androidUrlToGetPan($cardId: ID!) { urlToGetPan(cardId: $cardId) { url }}",
				"variables": {"cardId": card['id']},
				"extensions":{}
			}
			r = self.s.post(self.api_host, json=payload).json()

			r = self.s.get(r['data']['urlToGetPan']['url']).json()

			digits.append(
				{
					"id": card['id'],
					"owner": r['card_name'],
					"owner_client_code": r['card_client_code'],

					"number": r['card_pan'],
					"exp_date": r['card_exp_date'],
					"cvv": r['card_cvc2']
				}
			)

		return digits

	@property
	def used_for_topup(self):
		payload = {
			"query": "query androidListTopupCard { me { topupCards { ... Topup_TopupCardParts } }}\n\n"
				"fragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['topupCards']

	@property
	def default_used_for_topup(self):
		cards = self.used_for_topup
		for card in cards:
			if card['default']:
				return card

	def block_by_id(self, card_id):
		payload = {
			"query": "mutation androidUpdateCard($input: UpdateCardInput!) { updateCard(input: $input) { card { ... Card_CardParts } errors { path message} }}\n\n"
				"fragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}",
			"variables": {"input": {"cardId": card_id, "attributes": {"blocked": True}}},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		if not r['data']['updateCard']['card']['blocked']:
			raise Exception(r['data']['updateCard']['errors'])

	def unblock_by_id(self, card_id):
		payload = {
			"query": "mutation androidUpdateCard($input: UpdateCardInput!) { updateCard(input: $input) { card { ... Card_CardParts } errors { path message} }}\n\n"
				"fragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}",
			"variables": {"input": {"cardId": card_id, "attributes": {"blocked": False}}},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		if r['data']['updateCard']['card']['blocked']:
			raise Exception(r['data']['updateCard']['errors'])


class KardBankAccount(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } lockedTransactions } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['bankAccount']

	@property
	def id(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { bankAccount { id } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['bankAccount']['id']

	@property
	def iban(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { bankAccount { iban bic } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['bankAccount']

	@property
	def balance(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { bankAccount { balance { value currency { symbol isoCode } } } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['bankAccount']['balance']['value']


class KardSubscription(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { subscription { id status cancelledAt cancellationReason nextBilling { date amount { value } } plan { __typename id periodUnit name providerId price { value } } } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['subscription']

	@property
	def is_active(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { subscription { status cancelledAt } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return True if r['data']['me']['subscription']['status'] == "ACTIVE" else False

	@property
	def is_free_karder(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { subscription { plan { __typename name } } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		if r['data']['me']['subscription']['plan']['__typename'] == "LegacyPlan":
			# double check, probably pointless
			if r['data']['me']['subscription']['plan']['name'] == "Free Karder":
				return True
		return False

	@property
	def price(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { subscription { plan { periodUnit price { value } } } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		
		price = r['data']['me']['subscription']['plan']['price']['value']
		period = r['data']['me']['subscription']['plan']['periodUnit']

		return f"{price}€/{period.lower()}"

	@property
	def next_billing(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { subscription { nextBilling { date amount { value } } } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['subscription']['nextBilling']


class KardCashback(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { cashbackEnabled cashbackWallet { id balance { value currency { symbol isoCode } } amountEarned { value currency { symbol isoCode } } transactions(first: 10, order: CREATED, direction: DESC) { pageInfo { endCursor hasNextPage } nodes { ... Transaction_TransactionCashbackParts } } } }"
				"fragment Transaction_TransactionCashbackParts on Transaction { id title amount { value currency { symbol } } image { id url } processedAt category { name color image { url } } ... on CashbackTransaction { cashback { status brandLogo brandName sourceTransaction { id title image { id url } category { name color image { url } } amount { value currency { symbol } } } } }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r

	@property
	def is_cashback_active(self):
		payload = {
			"query": "query androidMe {me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { cashbackEnabled }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['cashbackEnabled']

	@property
	def total_earned(self):
		payload = {
			"query": "query androidMe {me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { cashbackWallet { amountEarned { value currency { symbol isoCode } } } }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['cashbackWallet']['amountEarned']['value']

	@property
	def pending_cashout(self):
		payload = {
			"query": "query androidMe {me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { cashbackWallet { balance { value currency { symbol isoCode } } } }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['cashbackWallet']['balance']['value']

	@property
	def transactions(self, limit: int=10):
		payload = {
			"query": "query androidMe {me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { cashbackWallet { transactions(first: "+str(limit)+", order: CREATED, direction: DESC) { pageInfo { endCursor hasNextPage } nodes { ... Transaction_TransactionCashbackParts } } } }"
				"fragment Transaction_TransactionCashbackParts on Transaction { id title amount { value currency { symbol } } image { id url } processedAt category { name color image { url } } ... on CashbackTransaction { cashback { status brandLogo brandName sourceTransaction { id title image { id url } category { name color image { url } } amount { value currency { symbol } } } } }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['cashbackWallet']['transactions']['nodes']

	@property
	def current_offers(self):
		payload = {
			"query": "query androidOffers { cashbackOffers { name url cashbackRate channel description legalTerms isConsumed maxPerUser brand { name logoUrl description } minAmount maxAmount pictureUrl startDate endDate } }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['cashbackOffers']

		#[{'name': 'SNCF Connect', 'url': 'https://www.sncf-connect.com/home?wiz_medium=part&wiz_source=paylead&wiz_campaign=fr_not__cashback__tr-multiproduit__mk_202204&wiz_content=__cpa', 'cashbackRate': 2.0, 'channel': 'ONLINE', 'description': 'Nouveau client SNCF Connect ? Profite dès maintenant de 2% de cashback sur ta 1ère commande !', 'legalTerms': "Offre de remboursement valable du 08/04/22 au 08/07/22, ou jusqu'à épuisement du budget, pour tout premier achat sur l'application SNCF Connect ou sur le site web https://www.sncf-connect.com", 'isConsumed': False, 'maxPerUser': 1, 'brand': {'name': 'SNCF Connect', 'logoUrl': 'https://static.prod.paylead.fr/images/c163dd86-38a7-48ff-8187-f976cf26cb6e.jpeg?1649343444', 'description': "SNCF Connect, c'est la nouvelle plateforme de voyages tout-en-un : planifiez, réservez et gérez tous vos trajets, petits et grands, en toute sérénité. SNCF Connect vous accompagne de bout en bout, en temps réel et à toutes les étapes de votre voyage."}, 'minAmount': 0.0, 'maxAmount': None, 'pictureUrl': 'https://static.prod.paylead.fr/images/ab97355f-28a5-4f88-8e41-07248061dcea.jpeg?1649413601', 'startDate': '2022-04-08T00:00:00Z', 'endDate': '2022-07-08T21:59:59Z'}]

	def cashout(self):
		#todo
		pass



k = Kard()
k.init()
print( k.cashback.current_offers )