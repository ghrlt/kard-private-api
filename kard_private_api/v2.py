import os
import json
import uuid
import requests


path = os.getcwd()


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

		self.subscription = KardSubscription()
		self.cashback = KardCashback()
		self.account = KardAccount()
		self.vaults = KardVaults()
		self.cards = KardCards()
		self.money = KardMoney()
		self.family = KardFamily()
		self.bank = KardBankAccount()
		self.contacts = KardContacts()
		self.transactions = KardTransactions()


class KardLocalSecrets(Kard):
	def __init__(self):
		if not 'secrets.json' in os.listdir(path):
			with open(path+'secrets.json', 'w') as f:
				f.write("{}")

		with open(path+'secrets.json', 'r') as f:
			secrets = json.load(f)

		self.vendor_identifier = secrets.get('vendorIdentifier')
		self.user_agent = secrets.get('userAgent')
		self.access_token = secrets.get('accessToken')
		self.refresh_token = secrets.get('refreshToken')
		self.pin_code = secrets.get('accountPin') or input("Please input your pin: ")
		self.phone_number = secrets.get('accountTel') or input("Please input your tel: ")

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

		with open(path+'secrets.json', 'w') as f:
			json.dump(new_secrets, f, indent=2)


class KardLogin(Kard):
	def __init__(self):
		super().__init__()

		if self.secrets.access_token:
			if self.is_still_logged_in:
				self.is_logged_in = True
				return

		self.init_login()

	@property
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
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { firstName } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['profile']['firstName']
	
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
	def birthdate(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { birthday } }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['profile']['birthday']

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

	def set_access_pin_code(self, new_pin):
		payload = {
			"query": "mutation androidSetPasscode($input: SetPasscodeInput!) { setPasscode(input: $input) { passcodeSet errors { path message } }}",
			"variables": {
				"input": {"passcode": new_pin}
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

	def reset_pin_code(self, _input=None, step=1):
		#_input, for step 1 should be birthdate, in yyyy-mm-dd format
		#		for step 2 should be OTP codee received by sms
		#		for step 3 should be the new 4 digits pin

		# --> If someone has a better way to handle this 3 step function, lmk <--

		if step == 1:
			payload = {
				"query": "mutation androidForgotPasscode($phoneNumber: PhoneNumber!, $dateOfBirth: ISO8601Date!) { forgotPasscode(input: { phoneNumber: $phoneNumber, dateOfBirth: $dateOfBirth }) { errors { message path } nextRetryAt }}",
				"variables": {
					"dateOfBirth": _input or KardAccount().birthdate,
					"phoneNumber": self.secrets.phone_number
				},
				"extensions": {}
			}
		elif step == 2:
			payload = {
				"query": "mutation androidVerifyPasscodeForgottenOtp($phoneNumber: PhoneNumber!, $code: String!) { verifyPasscodeForgottenOtp(input: { phoneNumber: $phoneNumber, code: $code }) { errors { message path } }}",
				"variables": {
					"phoneNumber": self.secrets.phone_number,
					"code": _input
				},
				"extensions": {}
			}
			self.temp_otp = _input

		elif step == 3:
			payload = {
				"query": "mutation androidChangePasscode($phoneNumber: PhoneNumber!, $code: String!, $newPasscode: Passcode!) { changePasscode(input: { code: $code, phoneNumber: $phoneNumber, newPasscode: $newPasscode }) { errors { message path } }}",
				"variables": {
					"newPasscode": _input,
					"phoneNumber": self.secrets.phone_number,
					"code": self.temp_otp
				},
				"extensions": {}
			}

		else:
			return {"errors": [{"message": "wtf is that step?"}]}

		r = self.s.post(self.api_host, json=payload).json()

		return r


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
	def raw_price(self):
		price = self.price

		return float(price.split('€')[0])

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


class KardIntercomMessenger(Kard):
	def __init__(self):
		super().__init__()

		#todo

		"""
		METHOD		POST
		URL 		https://bepnqfe3-android.mobile-messenger.intercom.com/messenger/mobile/open
		HEADERS
			accept-encoding: gzip
			accept-language: fr-
			authorization: Basic YmVwbnFmZTM...IyMg==
			connection: Keep-Alive
			content-length: 211
			content-type: application/json
			host: bepnqfe3-android.mobile-messenger.intercom.com
			idempotency-key: aa8d1370fa7778ad
			user-agent: okhttp/4.9.0
			x-intercom-agent: intercom-android-sdk/10.6.0
			x-intercom-host-app-version: 2022.08
			x-intercom-supported-languages: ar,bg,bs,ca,cs,da,de,de-form,el,es,et,fi,fr,he,hr,hu,id,it,ja,ko,lt,lv,mn,nb,nl,pl,pt-PT,pt-BR,ro,ru,sl,sr,sv,tr,vi,zh-Hant,zh-Hans
		JSON
			{
				"email": "urmail@mail.com",
				"hmac": "911e5...0b59ac493",
				"type": "user",
				"intercom_id": "6234a6...36a",
				"user_id": "9a...7-b231-44f0-9980-48...4c"
			}


		# Send 1st msg
		METHOD		POST
		URL 		https://bepnqfe3-android.mobile-messenger.intercom.com/messenger/mobile/conversations
		HEADERS
			same, but idempotency-key change (each req)
		JSON
			{
			  "app_id": "bepnqfe3",
			  "bot_intro": "",
			  "composer_suggestions": "[]",
			  "hmac": "911e5d...9ac493",
			  "user": {
			    "email": "urmail@mail.com",
			    "type": "user",
			    "intercom_id": "623...36a",
			    "user_id": "9a...87-b231-44f0-9980-481a...4c"
			  },
			  "blocks": [
			    {
			      "text": "J'aimerais avoir les marques suivantes dans mes KarDeals : OVH & Hyper U",
			      "type": "paragraph"
			    }
			  ]
			}

		RESPONSE
			{
			  "id": "41964",
			  "read": true,
			  "dismissed": false,
			  "participants": [
			    {
			      "id": "623...36a",
			      "avatar": {
			        "initials": "GH",
			        "color": "ffb3c6",
			        "image_urls": {}
			      },
			      "type": "user",
			      "name": "Gaëtan Hrlt",
			      "first_name": "Gaëtan",
			      "email": "urmail@mail.com"
			    }
			  ],
			  "conversation_parts": [
			    {
			      "id": "127...35",
			      "participant_id": "623...36a",
			      "participant_is_admin": false,
			      "body": [
			        {
			          "type": "paragraph",
			          "text": "J'aimerais avoir les marques suivantes dans mes KarDeals : OVH &amp; Hyper U"
			        }
			      ],
			      "is_initial_message": true,
			      "attachments": [],
			      "message_style": "chat",
			      "show_created_at": true,
			      "created_at": 1650719730,
			      "summary": "J'aimerais avoir les marques suivantes dans mes KarDeals : OVH & Hyper U",
			      "delivery_option": "summary",
			      "reply_type": "text",
			      "reply_options": [],
			      "seen_by_admin": "unseen"
			    }
			  ],
			  "user_participated": true,
			  "group_conversation_participant_ids": [],
			  "operator_client_conditions": [],
			  "intercom_link_solution": "live-chat",
			  "composer_state": {
			    "visible": true,
			    "version": 0,
			    "self_serve_suggestions_enabled": false,
			    "custom_bot_active": false,
			    "workflow_active": false
			  },
			  "prevent_end_user_replies": false,
			  "inbound_conversations_disabled": false,
			  "notification_status": "unknown",
			  "state": "state_open",
			  "is_inbound": true,
			  "config": {
			    "name": "Kard",
			    "base_color": "#7800F0",
			    "audio_enabled": false,
			    "show_powered_by": false,
			    "id_code": "bepnqfe3",
			    "welcome_message": [
			      {
			        "type": "paragraph",
			        "text": "C'est ici que nous répondons à toutes les questions !"
			      }
			    ],
			    "welcome_message_plain_text": "C'est ici que nous répondons à toutes les questions !",
			    "auto_response": "We'll notify you here and by email when we reply.",
			    "inbound_messages": true,
			    "real_time": true,
			    "is_first_request": false,
			    "real_time_config": {
			      "endpoints": [
			        "https://nexus-websocket-a.intercom.io/pubsub/5-z9A-XlMn9B93o...CY2p"
			      ],
			      "presence_heartbeat_interval": 30,
			      "connection_timeout": 70
			    },
			    "locale": "fr",
			    "metrics_enabled": true,
			    "background_requests_enabled": true,
			    "polling_interval": 7889238,
			    "no_real_time_throttle": 60,
			    "user_update_dup_cache_max_age": 600,
			    "local_rate_limit_period": 60,
			    "local_rate_limit": 100,
			    "new_session_threshold": 20,
			    "soft_reset_timeout": 1,
			    "help_center_url": "https://intercom.help/kardeu",
			    "help_center_urls": [
			      "https://intercom.help/kardeu",
			      "https://aide.kard.eu"
			    ],
			    "help_center_base_color": "#7800F0",
			    "help_center_locale": "fr",
			    "features": [],
			    "secondary_color": "#7800F0",
			    "primary_color_render_dark_text": false,
			    "secondary_color_render_dark_text": false,
			    "help_center_color_render_dark_text": false,
			    "team_intro": "C'est ici que nous répondons à toutes les questions !",
			    "team_greeting": "Hello Gaëtan 👋",
			    "launcher_bottom_padding": 16,
			    "launcher_alignment": "right",
			    "identity_verification_enabled": true,
			    "user_conversation_attachments_enabled": true,
			    "user_conversation_gifs_enabled": true,
			    "access_to_teammate_enabled": true,
			    "help_center_require_search": false,
			    "upload_size_limit": 41943040,
			    "prevent_multiple_inbound_conversations_enabled": true
			  },
			  "user": {
			    "type": "user",
			    "intercom_id": "623...36a",
			    "encrypted_user_id": "RXpzaHE0...dz09--34318f3...fb497",
			    "email": "gaetan.hrlt@gmail.com",
			    "user_id": "9a...87-b231-44f0-9980-481...4c"
			  },
			  "has_conversations": true
			}


		# Receive response
		METHOD		POST
		URL 		https://bepnqfe3-android.mobile-messenger.intercom.com/messenger/mobile/users
		HEADERS
			same
		JSON
			{
			  "user_attributes": {},
			  "hmac": "911e...9ac493",
			  "new_session": true,
			  "user": {
			    "email": "urmail@mail.com",
			    "type": "user",
			    "intercom_id": "623...36a",
			    "user_id": "9a...87-b231-44f0-9980-48...4c"
			  },
			  "sent_from_background": false,
			  "carousel_visible": false,
			  "device_data": {
			    "browser": "Intercom-Android-SDK",
			    "platform": "PULP 4G",
			    "language": "français",
			    "application_id": "eu.kard.android",
			    "application": "Kard",
			    "platform_version": "5.1.1",
			    "version": "2022.08"
			  }
			}
		RESPONSE
			{
			  "unread_conversations": {
			    "conversations": [
			      {
			        "id": "41964",
			        "read": false,
			        "dismissed": false,
			        "participants": [
			          {
			            "id": "5355934",
			            "avatar": {
			              "initials": "K",
			              "color": "ffb3c6",
			              "image_urls": {
			                "square_25": "https://static.intercomassets.com/avatars/5355934/square_25/Kard_Mascot_Guns_PostProd-1647278356.png",
			                "square_50": "https://static.intercomassets.com/avatars/5355934/square_50/Kard_Mascot_Guns_PostProd-1647278356.png",
			                "square_128": "https://static.intercomassets.com/avatars/5355934/square_128/Kard_Mascot_Guns_PostProd-1647278356.png"
			              },
			              "image_url": "https://static.intercomassets.com/avatars/5355934/square_128/Kard_Mascot_Guns_PostProd-1647278356.png"
			            },
			            "type": "admin",
			            "name": "Kardy",
			            "first_name": "Kardy",
			            "email": "hello@kard.eu",
			            "is_bot": false
			          },
			          {
			            "id": "623...36a",
			            "avatar": {
			              "initials": "GH",
			              "color": "ffb3c6",
			              "image_urls": {}
			            },
			            "type": "user",
			            "name": "Gaëtan Hrlt",
			            "first_name": "Gaëtan",
			            "email": "urmail@mail.com"
			          }
			        ],
			        "conversation_parts": [
			          {
			            "id": "14391724891",
			            "participant_id": "5355934",
			            "participant_is_admin": true,
			            "body": [
			              {
			                "type": "paragraph",
			                "text": "Un grand Merci pour tes suggestions 💜"
			              },
			              {
			                "type": "paragraph",
			                "text": "Nous les transmettons immédiatement à notre équipe en charge des partenariats. Peut être que ces marques feront partie des prochains deals 🤞"
			              },
			              {
			                "type": "paragraph",
			                "text": "Pense à regarder régulièrement tes KarDeals pour connaitre toutes les offres en cours 👀"
			              },
			              {
			                "type": "paragraph",
			                "text": "Si tu as des questions, n'hésite pas, on est là pour toi !"
			              }
			            ],
			            "is_initial_message": false,
			            "attachments": [],
			            "message_style": "open",
			            "show_created_at": true,
			            "created_at": 1650719736,
			            "summary": "Un grand Merci pour tes suggestions 💜 Nous les transmettons immédiatement à notre équipe en charge des partenariats. Peut être que ces marques feront partie des prochains deals 🤞 Pense à regarder régulièrement tes KarDeals pour connaitre toutes les offres en cours 👀 Si tu as des questions, n'hésite ",
			            "event_data": {},
			            "reply_options": [],
			            "seen_by_admin": "seen"
			          }
			        ],
			        "last_participating_admin": {
			          "id": "5355934",
			          "type": "Admin",
			          "avatar": {
			            "initials": "K",
			            "color": "ffb3c6",
			            "image_urls": {
			              "square_25": "https://static.intercomassets.com/avatars/5355934/square_25/Kard_Mascot_Guns_PostProd-1647278356.png",
			              "square_50": "https://static.intercomassets.com/avatars/5355934/square_50/Kard_Mascot_Guns_PostProd-1647278356.png",
			              "square_128": "https://static.intercomassets.com/avatars/5355934/square_128/Kard_Mascot_Guns_PostProd-1647278356.png"
			            },
			            "image_url": "https://static.intercomassets.com/avatars/5355934/square_128/Kard_Mascot_Guns_PostProd-1647278356.png"
			          },
			          "name": "Kardy",
			          "is_admin": true,
			          "first_name": "Kardy",
			          "last_active_at": 1650719736,
			          "is_active": false,
			          "is_bot": false,
			          "is_self": false,
			          "location": {
			            "city_name": "",
			            "country_name": "France",
			            "country_code": "FR",
			            "timezone": "Europe/Paris",
			            "timezone_offset": 7200
			          },
			          "social_accounts": [],
			          "initial": "K"
			        },
			        "user_participated": true,
			        "group_conversation_participant_ids": [],
			        "operator_client_conditions": [],
			        "intercom_link_solution": "live-chat",
			        "composer_state": {
			          "visible": true,
			          "version": 0,
			          "self_serve_suggestions_enabled": false,
			          "custom_bot_active": false,
			          "workflow_active": false
			        },
			        "prevent_end_user_replies": false,
			        "inbound_conversations_disabled": false,
			        "notification_status": "unknown",
			        "state": "state_closed",
			        "is_inbound": true
			      }
			    ],
			    "unread_conversation_ids": [
			      "41964"
			    ],
			    "total_count": 1
			  },
			  "composer_suggestions": {},
			  "bot_intro": {},
			  "team_presence": {
			    "active_admins": [
			      {
			        "id": "5409338",
			        "first_name": "Léo",
			        "avatar": {
			          "initials": "L",
			          "color": "c8c6c4",
			          "image_urls": {
			            "square_25": "https://static.intercomassets.com/avatars/5409338/square_25/Leo-Kard-1645026522.png",
			            "square_50": "https://static.intercomassets.com/avatars/5409338/square_50/Leo-Kard-1645026522.png",
			            "square_128": "https://static.intercomassets.com/avatars/5409338/square_128/Leo-Kard-1645026522.png"
			          },
			          "image_url": "https://static.intercomassets.com/avatars/5409338/square_128/Leo-Kard-1645026522.png"
			        },
			        "has_photo_avatar": true,
			        "name": "Léo"
			      },
			      {
			        "id": "5355934",
			        "first_name": "Kardy",
			        "avatar": {
			          "initials": "K",
			          "color": "ffb3c6",
			          "image_urls": {
			            "square_25": "https://static.intercomassets.com/avatars/5355934/square_25/Kard_Mascot_Guns_PostProd-1647278356.png",
			            "square_50": "https://static.intercomassets.com/avatars/5355934/square_50/Kard_Mascot_Guns_PostProd-1647278356.png",
			            "square_128": "https://static.intercomassets.com/avatars/5355934/square_128/Kard_Mascot_Guns_PostProd-1647278356.png"
			          },
			          "image_url": "https://static.intercomassets.com/avatars/5355934/square_128/Kard_Mascot_Guns_PostProd-1647278356.png"
			        },
			        "has_photo_avatar": true,
			        "name": "Kardy"
			      },
			      {
			        "id": "5409418",
			        "first_name": "Salma",
			        "avatar": {
			          "initials": "S",
			          "color": "6b9cff",
			          "image_urls": {
			            "square_25": "https://static.intercomassets.com/avatars/5409418/square_25/Salma-Kard-1647421939.png",
			            "square_50": "https://static.intercomassets.com/avatars/5409418/square_50/Salma-Kard-1647421939.png",
			            "square_128": "https://static.intercomassets.com/avatars/5409418/square_128/Salma-Kard-1647421939.png"
			          },
			          "image_url": "https://static.intercomassets.com/avatars/5409418/square_128/Salma-Kard-1647421939.png"
			        },
			        "has_photo_avatar": true,
			        "name": "Salma"
			      },
			      {
			        "id": "5409493",
			        "first_name": "Zahra",
			        "avatar": {
			          "initials": "Z",
			          "color": "0accac",
			          "image_urls": {
			            "square_25": "https://static.intercomassets.com/avatars/5409493/square_25/IMG_7939-1644920733.jpg",
			            "square_50": "https://static.intercomassets.com/avatars/5409493/square_50/IMG_7939-1644920733.jpg",
			            "square_128": "https://static.intercomassets.com/avatars/5409493/square_128/IMG_7939-1644920733.jpg"
			          },
			          "image_url": "https://static.intercomassets.com/avatars/5409493/square_128/IMG_7939-1644920733.jpg"
			        },
			        "has_photo_avatar": true,
			        "name": "Zahra"
			      },
			      {
			        "id": "5123148",
			        "first_name": "Kevin",
			        "avatar": {
			          "initials": "K",
			          "color": "ffb848",
			          "image_urls": {
			            "square_25": "https://static.intercomassets.com/avatars/5123148/square_25/Kevin-1641826041.png",
			            "square_50": "https://static.intercomassets.com/avatars/5123148/square_50/Kevin-1641826041.png",
			            "square_128": "https://static.intercomassets.com/avatars/5123148/square_128/Kevin-1641826041.png"
			          },
			          "image_url": "https://static.intercomassets.com/avatars/5123148/square_128/Kevin-1641826041.png"
			        },
			        "has_photo_avatar": true,
			        "name": "Kevin"
			      }
			    ],
			    "last_active": 1650720041,
			    "expected_response_delay": "Répond généralement dans un délai de quelques minutes",
			    "expected_response_delay_header": "Notre délai de réponse habituel",
			    "expected_response_delay_details": "Quelques minutes"
			  },
			  "config": {
			    "name": "Kard",
			    "base_color": "#7800F0",
			    "audio_enabled": false,
			    "show_powered_by": false,
			    "id_code": "bepnqfe3",
			    "welcome_message": [
			      {
			        "type": "paragraph",
			        "text": "C'est ici que nous répondons à toutes les questions !"
			      }
			    ],
			    "welcome_message_plain_text": "C'est ici que nous répondons à toutes les questions !",
			    "auto_response": "We'll notify you here and by email when we reply.",
			    "inbound_messages": true,
			    "real_time": true,
			    "is_first_request": false,
			    "real_time_config": {
			      "endpoints": [
			        "https://nexus-websocket-a.intercom.io/pubsub/5-zhQq...CvruY-IpHnFXZPG...f1f-PuSnlI...5Uq-KAuU-2aW...Zo"
			      ],
			      "presence_heartbeat_interval": 30,
			      "connection_timeout": 70
			    },
			    "locale": "fr",
			    "metrics_enabled": true,
			    "background_requests_enabled": true,
			    "polling_interval": 7889238,
			    "no_real_time_throttle": 60,
			    "user_update_dup_cache_max_age": 600,
			    "local_rate_limit_period": 60,
			    "local_rate_limit": 100,
			    "new_session_threshold": 20,
			    "soft_reset_timeout": 1,
			    "help_center_url": "https://intercom.help/kardeu",
			    "help_center_urls": [
			      "https://intercom.help/kardeu",
			      "https://aide.kard.eu"
			    ],
			    "help_center_base_color": "#7800F0",
			    "help_center_locale": "fr",
			    "features": [],
			    "secondary_color": "#7800F0",
			    "primary_color_render_dark_text": false,
			    "secondary_color_render_dark_text": false,
			    "help_center_color_render_dark_text": false,
			    "team_intro": "C'est ici que nous répondons à toutes les questions !",
			    "team_greeting": "Hello Gaëtan 👋",
			    "launcher_bottom_padding": 16,
			    "launcher_alignment": "right",
			    "identity_verification_enabled": true,
			    "user_conversation_attachments_enabled": true,
			    "user_conversation_gifs_enabled": true,
			    "access_to_teammate_enabled": true,
			    "help_center_require_search": false,
			    "upload_size_limit": 41943040,
			    "prevent_multiple_inbound_conversations_enabled": true
			  },
			  "user": {
			    "type": "user",
			    "intercom_id": "6234a6a20d73afe082e8836a",
			    "encrypted_user_id": "WllNT0o...4dz09--476...f0a",
			    "email": "urmail@mail.com",
			    "user_id": "9ac...87-b231-44f0-9980-48...4c"
			  },
			  "has_conversations": true
			}


		# Reply
		METHOD		POST
		URL 		https://bepnqfe3-android.mobile-messenger.intercom.com/messenger/mobile/conversations/41964/reply
		HEADERS
			same
		JSON
			{
			  "app_id": "bepnqfe3",
			  "hmac": "911e5d...9ac493",
			  "user": {
			    "email": "urmail@mail.com",
			    "type": "user",
			    "intercom_id": "6234a...36a",
			    "user_id": "9a...87-b231-44f0-9980-48...4c"
			  },
			  "type": "user",
			  "blocks": [
			    {
			      "text": "Merci !",
			      "type": "paragraph"
			    }
			  ],
			  "message_type": "comment"
			}
		RESPONSE
			{
			  "id": "1439...37",
			  "participant_id": "6234a...36a",
			  "participant_is_admin": false,
			  "body": [
			    {
			      "type": "paragraph",
			      "text": "Merci !"
			    }
			  ],
			  "is_initial_message": false,
			  "attachments": [],
			  "message_style": "open",
			  "show_created_at": true,
			  "created_at": 1650720162,
			  "summary": "Merci !",
			  "event_data": {},
			  "reply_options": [],
			  "seen_by_admin": "unseen",
			  "config": {
			    "name": "Kard",
			    "base_color": "#7800F0",
			    "audio_enabled": false,
			    "show_powered_by": false,
			    "id_code": "bepnqfe3",
			    "welcome_message": [
			      {
			        "type": "paragraph",
			        "text": "C'est ici que nous répondons à toutes les questions !"
			      }
			    ],
			    "welcome_message_plain_text": "C'est ici que nous répondons à toutes les questions !",
			    "auto_response": "We'll notify you here and by email when we reply.",
			    "inbound_messages": true,
			    "real_time": true,
			    "is_first_request": false,
			    "real_time_config": {
			      "endpoints": [
			        "https://nexus-websocket-a.intercom.io/pubsub/5-AlRpX...mp5P-aC...4gSQ-59STt...ToZ"
			      ],
			      "presence_heartbeat_interval": 30,
			      "connection_timeout": 70
			    },
			    "locale": "fr",
			    "metrics_enabled": true,
			    "background_requests_enabled": true,
			    "polling_interval": 7889238,
			    "no_real_time_throttle": 60,
			    "user_update_dup_cache_max_age": 600,
			    "local_rate_limit_period": 60,
			    "local_rate_limit": 100,
			    "new_session_threshold": 20,
			    "soft_reset_timeout": 1,
			    "help_center_url": "https://intercom.help/kardeu",
			    "help_center_urls": [
			      "https://intercom.help/kardeu",
			      "https://aide.kard.eu"
			    ],
			    "help_center_base_color": "#7800F0",
			    "help_center_locale": "fr",
			    "features": [],
			    "secondary_color": "#7800F0",
			    "primary_color_render_dark_text": false,
			    "secondary_color_render_dark_text": false,
			    "help_center_color_render_dark_text": false,
			    "team_intro": "C'est ici que nous répondons à toutes les questions !",
			    "team_greeting": "Hello Gaëtan 👋",
			    "launcher_bottom_padding": 16,
			    "launcher_alignment": "right",
			    "identity_verification_enabled": true,
			    "user_conversation_attachments_enabled": true,
			    "user_conversation_gifs_enabled": true,
			    "access_to_teammate_enabled": true,
			    "help_center_require_search": false,
			    "upload_size_limit": 41943040,
			    "prevent_multiple_inbound_conversations_enabled": true
			  },
			  "user": {
			    "type": "user",
			    "intercom_id": "6234a6a20d73afe082e8836a",
			    "encrypted_user_id": "WEpCL1R...QT09--8aca70...8be3df",
			    "email": "urmail@mail.com",
			    "user_id": "9a...87-b231-44f0-9980-48...4c"
			  },
			  "has_conversations": true
			}


		"""


class KardContacts(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		payload = {
			"query": "query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username hasBankAccount } } }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']

	@property
	def with_kard_account(self):
		contacts = self.complete_data
		res = []
		for contact in self.complete_data['contacts']:
			if contact['status']:
				res.append(contact)

		return res

	@property
	def friends(self):
		payload = {
			"query": "query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['friendships']

	def remove_friend(self, friend_id):
		payload = {
			"query": "mutation androidCancelFriend($userId: ID!) { cancelFriendship(input: {userId: $userId}) { errors { message path } }}",
			"variables": {"userId": friend_id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		
		return r.get('errors') or r['data']['cancelFriendship']['errors']

	def send_friend_request(self, friend_id):
		payload = {
			"query": "mutation androidRequestFriendship($userId: ID!) { requestFriendship(input: {userId: $userId}) { errors { message path } }}",
			"variables": {"userId": friend_id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		
		return r['data']['requestFriendship']['errors']

	def reject_friend_request(self, friend_id):
		payload = {
			"query": "mutation androidRefuseFriendship($userId: ID!) { refuseFriendship(input: {userId: $userId}) { errors { message path } }}",
			"variables": {"userId": friend_id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		
		return r.get('errors') or r['data']['refuseFriendship']['errors']

	def accept_friend_request(self, friend_id):
		payload = {
			"query": "mutation androidAcceptFriend($userId: ID!) { acceptFriendship(input: {userId: $userId}) { errors { message path } }}",
			"variables": {"userId": friend_id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		
		return r.get('errors') or r['data']['acceptFriend']['errors']


class KardFamily(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		payload = {
			"query": "query androidFamily { me { family { ... Family_FamilyParts } }}\n\n"
				"fragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\n\n"
				"fragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\n\n"
				"fragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked scheme ... on PhysicalCard { atm contactless swipe online design orderedAt }}\n\n"
				"fragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value rejectionReason } identityVerification { status url rejectionReason score } proofOfAddress { status files { contentType url ... on Image { width height } } rejectionReason } canStart lastRejectedIdentityVerification { status url rejectionReason score} nbOfRejectedIdentityVerifications}\n\n"
				"fragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name providerId price { value } }}\n\n"
				"fragment Family_MeParts on Me { id type createdAt profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } card { id } canOrderCard cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } cards { nodes { ... Card_CardParts } } email claimId canOrderCard phoneNumber bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } lockedTransactions } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } subscription { ... Me_SubscriptionParts } onboardingDone savingsAmount { value } topupIncentiveActivated noPhoneNumber currentSpendings { monthlyPos { value } weeklyPos { value } weeklyAtm { value } monthlyAtm { value } } transactionLimits { id amount { value currency { symbol } } recurrence transactionType }}\n\n"
				"fragment Family_FamilyParts on Family { memberships { status primary type nickname member { ... Family_MeParts } }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()
		return r['data']['me']['family']['memberships']

	@property
	def parents(self):
		members = self.complete_data
		parents = []

		for member in members:
			if member['type'] == "PARENT":
				parents.append(member)

		return parents

	@property
	def siblings(self):
		members = self.complete_data
		siblings = []

		for member in members:
			if member['type'] != "PARENT":
				siblings.append(member)

		return siblings

	def set_parent_nickname(self, parent_id, nickname: str):
		payload = {
			"query": "mutation androidUpdateNickname($parentId: ID!, $nickname: String!) { updateNickname(input: {parentId: $parentId, nickname: $nickname}) { errors { message path } }}",
			"variables": {
				"nickname": nickname,
				"parentId": parent_id
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

		#if user_id not parent id -> {'errors': ['You are not allowed to do this']}


class KardTransactions(Kard):
	def __init__(self):
		super().__init__()

	@property
	def complete_data(self):
		# Voluntarily not putting friends public transactions
		# as it is a discontinued feature in the app, and so might soon be in the API

		return self.get_all()

	def get(self, limit: int, after: str):
		payload = {
			"query": "query androidTransactions($first: Int, $after: String) { me { bankAccount { balance { value } } typedTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title status visibility amount { value currency { symbol } } category { name color image { url } } user { id firstName lastName username } processedAt ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on CardTransaction { card { ... Card_CardParts } mobilePaymentProvider cashback { id status brandLogo brandName amount { value currency { symbol } } } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } ... on TopupTransaction { sender { nickname member { id profile { firstName } } } message } ... on RejectedTransaction { rejectionReason } ... on CashbackTransaction { cashback { id status brandLogo brandName amount { value currency { symbol } } sourceTransaction { id title image { id url } category { name color image { url } } amount { value currency { symbol } } } } } } } typedFriendsTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title category { name image { url } } processedAt user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } ... on TopupTransaction { sender { nickname member { id profile { firstName } } } message } } } }}\n\nfragment Vault_VaultMiniParts on Vault { name color emoji { name unicode }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked scheme ... on PhysicalCard { atm contactless swipe online design orderedAt }}",
			"variables": {
				"after": after,
				"first": limit
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		transactions = r['data']['me']['typedTransactions']['nodes']
		return transactions, r['data']['me']['typedTransactions']['pageInfo']['endCursor']

	def get_all(self, explicit_refresh: bool=False):
		cursor = None
		transactions = []

		# This is a necessity to avoid API spam & avoid Memory/Speed issues
		if not explicit_refresh:
			try: return self.all
			except: pass

		while True:
			r = self.get(20, cursor)
			cursor = r[1]

			#for t in r[0]:
			#	print(t['id'], t['title'], t['processedAt'])

			if r[0]:
				if transactions and transactions[-1]['id'] == r[0][0]['id']:
					break
				else:
					transactions += r[0]
			else:
				break

		self.all = transactions
		return transactions

	@property
	def incoming(self):
		incoming_transactions = []

		for transaction in self.get_all():
			if transaction['amount']['value'] > 0:
				incoming_transactions.append(transaction)

		return incoming_transactions
	
	@property
	def outgoing(self):
		outgoing_transactions = []

		for transaction in self.get_all():
			if transaction['amount']['value'] < 0:
				outgoing_transactions.append(transaction)

		return outgoing_transactions

	@property
	def internal(self):
		internal_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] in ["InternalTransferTransaction", "ClosingAccountTransaction"]:
				internal_transactions.append(transaction)

		return internal_transactions

	@property
	def through_p2p(self):
		p2p_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] == "P2pTransaction":
				p2p_transactions.append(transaction)

		return p2p_transactions
	
	@property
	def through_card(self):
		card_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] == "CardTransaction":
				card_transactions.append(transaction)

		return card_transactions

	@property
	def through_banktransfer(self):
		banktransfer_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] == "BankTransaction":
				banktransfer_transactions.append(transaction)

		return banktransfer_transactions

	@property
	def from_slash(self):
		slash_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] == "MoneyLinkTransaction":
				slash_transactions.append(transaction)

		return slash_transactions
	
	@property
	def topups(self):
		topup_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] == "TopupTransaction":
				topup_transactions.append(transaction)

		return topup_transactions

	@property
	def rejected(self):
		rejected_transactions = []

		for transaction in self.get_all():
			if transaction['__typename'] == "RejectedTransaction":
				rejected_transactions.append(transaction)

		return rejected_transactions


	def edit_title(self, transaction_id, new_name: str):
		payload = {
			"query": "mutation androidUpdateTransaction($input: UpdateTransactionInput!) { updateTransaction(input: $input) { errors { message path } } }",
			"variables": {
				"input": {
					"transactionId": transaction_id,
					"attributes": {"title": new_name}
				}
			},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()
		
		return r


class KardMoney(Kard):
	def __init__(self):
		super().__init__()

	@property
	def balance(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { bankAccount { balance { value } }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['bankAccount']['balance']['value']

	@property
	def receive_methods(self):
		d = {
			"bankTransfer": {
				**KardBankAccount().iban,
				"rib": self.s.get(f"https://api.kard.eu/bank_account_details/{KardBankAccount().id}.pdf").content
			},
			"slashLink": f"https://s.kard.eu/{KardAccount().username}"
		}

		return d

	@property
	def _incoming_requests(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['pendingDebts']

	@property
	def outgoing_requests(self):
		#todo

		# Seems that we cannot know this | At least not for the ones sent to other children

		pass

	def send(self, friend_id, amount: float, reason: str):
		payload = {
			"query": "mutation androidSendMoney($input: SendMoneyInput!) { sendMoney(input: $input) { errors { path message } } }",
			"variables": {
				"input": {
					"internalUsersIds": [friend_id],
					"externalUsers": [],
					"amount": {"value": amount, "currency": "EUR"},
					"reason": "reason"
				}
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

	def topup_from_saved_card(self, amount: float, card_providerSourceId: str, card_cvv: str):
		payload = {
			"query": "mutation androidTopupAccount($paymentSource: PaymentSource!, $amount: AmountInput!, $cvv: Cvv!, $childId: ID, $recipientId: ID, $failureUrl: String, $successUrl: String, $message: MoneyLinkMessage!) { topupAccount(input: { paymentSource: $paymentSource, cvv: $cvv, amount: $amount, childId: $childId, recipientId: $recipientId, failureUrl: $failureUrl, successUrl: $successUrl, message: $message }) { paymentId secureFormUrl errors { message path } }}",
			"variables": {
				"childId": KardAccount().id,
				"amount": {"value": amount, "currency": "EUR"},
				"paymentSource": card_providerSourceId,
				"failureUrl": "https://eu.kard.app/3ds/failure",
				"cvv": card_cvv,
				"message": "",
				"successUrl": "https://eu.kard.app/3ds/success"
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		#return r['data']['topupAccount']['secureFormUrl']
		return r

		#{'data': {'topupAccount': {'paymentId': 'pay_bpd...hce6y', 'secureFormUrl': 'https://api.checkout.com/sessions-interceptor/sid_uy4...uby4', 'errors': []}}}
		#{'data': {'topupAccount': {'paymentId': None, 'secureFormUrl': None, 'errors': [{'message': 'Amount must be greater than or equal to 5', 'path': ['attributes', 'amount']}]}}}
		#{'errors': [{'message': 'Variable $amount of type AmountInput! was provided invalid value for value (Value has to be positive (received: -10))', 'locations': [{'line': 1, 'column': 62}], 'extensions': {'value': {'value': -10, 'currency': 'EUR'}, 'problems': [{'path': ['value'], 'explanation': 'Value has to be positive (received: -10)', 'message': 'Value has to be positive (received: -10)'}]}}]}

	def request_from_friend(self, friend_id, amount: float, reason: str="", currency: str="EUR"):
		payload = {
			"query": "mutation androidRequestMoney($input: RequestMoneyInput!) { requestMoney(input: $input) { errors { path message } }}",
			"variables": {
				"input": {
					"internalUsersIds": [friend_id],
					"externalUsers": [],
					"amount": {"value": amount, "currency": currency},
					"reason": reason
				}
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

		#{'data': {'requestMoney': {'errors': []}}}
		#{'errors': [{'message': 'Variable $input of type RequestMoneyInput! was provided invalid value for amount.value (Value has to be positive (received: -0.01))', 'locations': [{'line': 1, 'column': 30}], 'extensions': {'value': {'internalUsersIds': ['Z2lkOi8va2FyZC1hcGkvVXNlci8zOGFlNmJjOC1hNWIyLTRlZmQtOGRjOS1hZWYyN2VjYjA0ZTY'], 'externalUsers': [], 'amount': {'value': -0.01, 'currency': 'EUR'}, 'reason': 'test'}, 'problems': [{'path': ['amount', 'value'], 'explanation': 'Value has to be positive (received: -0.01)', 'message': 'Value has to be positive (received: -0.01)'}]}}]}

	def request_from_parent(self, amount: float, reason: str="", currency: str="EUR"):
		payload = {
			"query": "mutation androidAskParentForMoney($amount: AmountInput!, $parentId: ID!, $reason: String) { askParentForMoney(input: {amount: $amount, parentId: $parentId, reason: $reason}) { clientMutationId errors { message path } }}",
			"variables": {
				"amount": {"value": amount, "currency": currency},
				"parentId": KardFamily().parents[0]['id'], "reason": reason
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r


	def reject_request(self, request_id):
		payload = {
			"query": "mutation androidRejectMoneyRequest($moneyRequestId: ID!) { rejectMoneyRequest(input: {moneyRequestId: $moneyRequestId}) { errors { path message } }}",
			"variables": {"moneyRequestId": request_id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

	def accept_request(self, request_id):
		payload = {
			"query": "mutation androidAcceptMoneyRequest($moneyRequestId: ID!) { acceptMoneyRequest(input: {moneyRequestId: $moneyRequestId}) { errors { path message } }}",
			"variables": {"moneyRequestId": request_id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

		#{'data': {'acceptMoneyRequest': {'errors': []}}}
		#{'data': {'acceptMoneyRequest': {'errors': [{'path': ['attributes', 'max_outgoing_amount'], 'message': 'Cannot spend that much money'}]}}}


class KardActivities(Kard):
	def __init__(self):
		super().__init__()

		"""
		{
		  "query": "query androidGetActivityItems { activityItems { id onClickUrl title body icon isRead isDone createdAt device modal { title body buttonTitle onClickUrl kardy withCelebration } }}",
		  "variables": {},
		  "extensions": {}
		}
		RESPONSE
		{
		  "data": {
		    "activityItems": []
		  }
		}
		"""


class KardVaults(Kard):
	def __init__(self):
		super().__init__()

	@property
	def list(self):
		payload = {
			"query": "query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\n"
				"fragment Vault_VaultParts on Vault { id name color emoji { name unicode } goal { value } balance { value }}",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['vaults']

	@property
	def total_saved(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\n"
				"fragment Me_MeParts on Me { savingsAmount { value } }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['savingsAmount']['value']

	@property
	def save_goal(self):
		payload = {
			"query": "query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\n"
				"fragment Vault_VaultParts on Vault { goal { value } }",
			"variables": {},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return sum([v['goal']['value'] for v in r['data']['me']['vaults']])

	def create(self, name: str, goal: float, currency: str="EUR"):
		payload = {
			"query": "mutation androidCreateVault($goal: AmountInput!, $name: Name!) { createVault(input: {goal: $goal, name: $name}) { errors { message path } vault { id } }}",
			"variables": {
				"goal": {"value": goal, "currency": currency},
				"name": name
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['createVault']['vault'].get('id')

		#{'errors': [{'message': 'Variable $goal of type AmountInput! was provided invalid value for value (Value has to be positive (received: -1))', 'locations': [{'line': 1, 'column': 29}], 'extensions': {'value': {'value': -1, 'currency': 'EUR'}, 'problems': [{'path': ['value'], 'explanation': 'Value has to be positive (received: -1)', 'message': 'Value has to be positive (received: -1)'}]}}]}
		#{'errors': [{'message': 'Variable $goal of type AmountInput! was provided invalid value for value (Value is too high (received: 100000000))', 'locations': [{'line': 1, 'column': 29}], 'extensions': {'value': {'value': 100000000, 'currency': 'EUR'}, 'problems': [{'path': ['value'], 'explanation': 'Value is too high (received: 100000000)', 'message': 'Value is too high (received: 100000000)'}]}}]}

		# WARNING: You cannot put an amount of 0 BUT you can put an amount of 0.001 or lower
		# and the api call will work BUT, the api will return a goal value of 0 & your app will crash lol

	def get_object(self, vault_id):
		return KardVault(vault_id, [v for v in self.list if v['id'] == vault_id][0])

class KardVault(Kard):
	def __init__(self, vault_id, vault_obj):
		super().__init__()

		self._id = vault_id
		self._json = vault_obj

	@property
	def complete_data(self):
		d = {**self._json, "transactions": self.transactions}
		return d

	@property
	def transactions(self):
		return self.get_all_transactions()

	def get_transactions(self, limit: int, after: str):
		payload = {
			"query": "query androidGetVaultTransactions($vaultId: ID!, $first: Int, $after: String, $numberOfComments: Int) { vault(vaultId: $vaultId) { id transactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { ... Transaction_TransactionParts } } }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked scheme ... on PhysicalCard { atm contactless swipe online design orderedAt }}\n\nfragment Vault_VaultParts on Vault { id name color emoji { name unicode } goal { value } balance { value }}\n\nfragment Transaction_TransactionParts on Transaction { __typename id title status address image { id url } visibility amount { value currency { symbol } } category { name color image { url } } processedAt comments(first: $numberOfComments) { totalCount pageInfo { endCursor hasNextPage } nodes { id comment createdAt user { id firstName lastName avatar { url } } } } quickAnswers { message } user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on CardTransaction { card { ... Card_CardParts } mobilePaymentProvider cashback { id status brandLogo brandName amount { value currency { symbol } } } } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultParts } } ... on MoneyLinkTransaction { from message } ... on TopupTransaction { sender { nickname member { id profile { firstName } } } message } ... on RejectedTransaction { rejectionReason mobilePaymentProvider } ... on CashbackTransaction { cashback { id brandLogo brandName amount { value currency { symbol } } status sourceTransaction { id title amount { value currency { symbol } } } } } ... on GiftTransaction { amount { value } }}",
			"variables": {
				"numberOfComments": 0,
				"vaultId": self.id,
				"first": limit,
				"after": after
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		transactions = r['data']['vault']['transactions']['nodes']
		return transactions, r['data']['vault']['transactions']['pageInfo']['endCursor']

	def get_all_transactions(self, explicit_refresh: bool=False):
		cursor = None
		transactions = []

		# This is a necessity to avoid API spam & avoid Memory/Speed issues
		if not explicit_refresh:
			try: return self.all
			except: pass

		while True:
			r = self.get_transactions(10, cursor)
			cursor = r[1]

			#for t in r[0]:
			#	print(t['id'], t['title'], t['processedAt'])

			if r[0]:
				if transactions and transactions[-1]['id'] == r[0][0]['id']:
					break
				else:
					transactions += r[0]
			else:
				break

		self._all_transactions = transactions
		return transactions

	@property
	def id(self):
		return self._id
	
	@property
	def name(self):
		return self._json['name']

	@property
	def balance(self):
		return self._json['balance']['value']

	@property
	def goal(self):
		return self._json['goal']['value']

	@property
	def emote(self):
		return self._json['emoji']
	
	@property
	def emoji(self):
		return self.emote

	@property
	def color(self):
		return self._json['color']

	@property
	def colour(self):
		return self.color

	def add_money(self, amount: float, currency: str="EUR"):
		payload = {
			"query": "mutation androidTransferMoney($sourceId: ID, $destinationId: ID!,$amount: AmountInput!) { transferMoney(input: {sourceId: $sourceId, destinationId: $destinationId, amount: $amount}) { errors { message path } }}",
			"variables": {
				"amount": {"value": amount, "currency": currency},
				"sourceId": KardBankAccount().id, "destinationId": self.id
			},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r

	def edit_emote(self, emote: str):
		valid_emotes = ["🎁", "🎈", "🛍", "💰", "😈", "🎓", "🏝", "🎫", "🎸", "✈️", "👟", "📱", "🎮", "🛴", "🛵"]

		payload = {
		  "query": "mutation androidUpdateVault($vaultId: ID!, $color: HexadecimalColorCode, $emoji: EmojiInput, $name: Name) { updateVault(input: {vaultId: $vaultId, color: $color, emoji: $emoji, name: $name}) { errors { message path } vault { id name color emoji { name unicode } goal { value } balance { value } } }}",
		  "variables": {
		    "vaultId": self.id,
		    "emoji": emote
		  },
		  "extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		try: self._json = r['data']['updateVault']['vault']
		except: pass

		return r

		#{'errors': [{'message': 'Variable $emoji of type EmojiInput was provided invalid value', 'locations': [{'line': 1, 'column': 74}], 'extensions': {'value': '✈', 'problems': [{'path': [], 'explanation': '"✈" is not a valid emoji', 'message': '"✈" is not a valid emoji'}]}}]}

	def edit_color(self, color: str):
		official_colors = {
			"purpleblack": "#1f193f", 	"grey":"#75818c",
			"purplelight": "#bd3fdd",	"yellow":"#ffca10",
			"purpledark": "#9850ff",	"pink":"#f943b1",	
			"black": "#1b1d20", 		"green":"#3ce977",
			"orange":"#ff9455", 		"red": "#ff5f7c",
			"cyan":"#15e4da", 			"blue": "#35c4ff"
		} #Any hexadecimal code will work though! (Must provide in a 6+1char format!)
		
		if color in official_colors:
			color = official_colors[color]

		payload = {
		  "query": "mutation androidUpdateVault($vaultId: ID!, $color: HexadecimalColorCode, $emoji: EmojiInput, $name: Name) { updateVault(input: {vaultId: $vaultId, color: $color, emoji: $emoji, name: $name}) { errors { message path } vault { id name color emoji { name unicode } goal { value } balance { value } } }}",
		  "variables": {
		    "vaultId": self.id,
		    "color": color
		  },
		  "extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		try: self._json = r['data']['updateVault']['vault']
		except: pass
		
		return r

		#{'data': {'updateVault': {'errors': []}}}
		#{'errors': [{'message': 'Variable $color of type HexadecimalColorCode was provided invalid value', 'locations': [{'line': 1, 'column': 44}], 'extensions': {'value': '#0F0', 'problems': [{'path': [], 'explanation': '"#0F0" is not a valid hexadecimal color code', 'message': '"#0F0" is not a valid hexadecimal color code'}]}}]}

	def close(self):
		payload = {
			"query": "mutation androidCloseVault($vaultId: ID!) { closeVault(input: {vaultId: $vaultId}) { errors { message path } }}",
			"variables": {"vaultId": self.id},
			"extensions": {}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r
	

	def edit_colour(self, *args, **kwargs):
		return self.edit_color(*args, **kwargs)

	def edit_emoji(self, *args, **kwargs):
		return self.edit_emoji(*args, **kwargs)
	
	def topup(self, *args, **kwargs):
		return self.add_money(*args, **kwargs)

	def delete(self, *args, **kwargs):
		return self.close(*args, **kwargs)	
