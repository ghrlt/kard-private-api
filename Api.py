import json, time, datetime, base64, webbrowser
from requests import request

def readF(file):
	with open(f'{file}.json', 'r') as f:
		data = json.loads(f.read())

	return data

def writeF(file, data):
	with open(f'{file}.json', 'w') as f:
		json.dump(data, f, indent=2)

def getLastWeek():
	today = datetime.date.today()

	y = str(today).split('-')[0]
	m = str(today).split('-')[1]
	d = str(today).split('-')[2]
	day = "0"+str(int(d)-7)


	if day == "0-1":
		if int(m)%2 == 0 and not m == "03":
			d = "31"
		elif not m == "03":
			d = "30"
		else: #February
			if int(y)%400 == 0 or int(y)%4 == 0:
				d = "29"
			else:
				d = "28"

		m = "0"+str(int(m)-1)

	lastWeek = y+"-"+m+"-"+d

	return lastWeek, str(today)

def getLastMonth():
	today = datetime.date.today()

	y = str(today).split('-')[0]
	m = str(today).split('-')[1]
	d = "01"

	lastMonth = y+"-"+m+"-"+d

	return lastMonth, str(today)

def getLastYear():
	today = datetime.date.today()

	y = str(today).split('-')[0]
	m = "01"
	d = "01"

	lastYear = y+"-"+m+"-"+d

	return lastYear, str(today)

def getTotal():
	today = datetime.date.today()

	beginning = Account.creationDate()
	beginning = str(beginning.split("T")[0])

	return str(beginning), str(today)



global TOKEN
TOKEN = readF('config')['login']['token']
VENDORIDENTIFIER = readF('config')['login']['identifier']
USERAGENT = "Gaetan/911"

NUM = readF('config')['login']['phone']
CODE = readF('config')['login']['code']
HEADERS_NONAUTH = {
    'content-type': "application/json",
    'content-length': "666",
    'host': "api.kard.eu",
    'connection': "Keep-Alive",
    'accept-encoding': "gzip",
    'user-agent': USERAGENT,
    'vendoridentifier': VENDORIDENTIFIER,
    'accept-language': "en"
}
HEADERS = {
    "content-type": "application/json",
    "content-length": "666",
    "host": "api.kard.eu",
    "connection": "Keep-Alive",
    "accept-encoding": "gzip",
    'user-agent': USERAGENT,
    'vendoridentifier': VENDORIDENTIFIER,
    "authorization": "Bearer " + TOKEN,
    "accept-language": "en"
}
API_URL = "https://api.kard.eu/graphql"


#Login
def login(num=NUM, code=CODE):

	payload = {
	    "query": "mutation androidInitSession($createUser: Boolean, $phoneNumber: PhoneNumber!, $platform: DevicePlatform, $vendorIdentifier: String!) { initSession(input: {createUser: $createUser, phoneNumber: $phoneNumber, platform: $platform, vendorIdentifier: $vendorIdentifier}) { challenge expiresAt errors { path message } }}",
	    "variables": {"platform": "ANDROID", "createUser": True, "phoneNumber": num, "vendorIdentifier": VENDORIDENTIFIER},
	    "extensions": {}
	}

	response = request("POST", API_URL, json=payload, headers=HEADERS_NONAUTH)
	data = json.loads(response.text)
	
	try:
		err = data['errors']['extensions']['problems']['explanation']
		raise Exception(err)
	except:
		if data['data']['initSession']['challenge'] == "OTP":
			otp = input("You need to confirm OTP code sent to " + num + " : ")

			payload = {
			    "query": "mutation androidVerifyOTP($authenticationProvider: AuthenticationProviderInput, $code: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { verifyOtp(input: {authenticationProvider: $authenticationProvider, code: $code, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { challenge accessToken refreshToken errors { path message } }}",
			    "variables": {"phoneNumber": num,"vendorIdentifier": VENDORIDENTIFIER,"code": otp},
			    "extensions": {}
			}

			response = request("POST", API_URL, json=payload, headers=HEADERS_NONAUTH)
			data = json.loads(response.text)

		elif data['data']['initSession']['challenge'] == "PASSCODE":
			pass
		else:
			print('˄˄˄')
			print(data)
			print('˅˅˅')
			raise Exception('Never saw this. Open an issue with any previous text please.')

		try:
			passcode = data['data']['verifyOtp']['challenge']
		except: 
			pass

		payload = {
		    "query": "mutation androidSignIn($authenticationProvider: AuthenticationProviderInput,$passcode: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { signIn(input: {authenticationProvider: $authenticationProvider,passcode: $passcode, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { accessToken refreshToken errors { path message } }}",
		    "variables": {"passcode": code,"phoneNumber": num,"vendorIdentifier": VENDORIDENTIFIER},
		    "extensions": {}
		}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		access = data['data']['signIn']['accessToken']
		
		data = readF('config')
		data['login']['token'] = access
		writeF('config', data)


		TOKEN = access
		return access
	




'''
	Get account information (Child)
'''
class Account:

	#get account creation date
	def creationDate():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { createdAt }","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['createdAt'] #Formatting?

	#get account id
	def id():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { id }","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['id']

	#get account avatar
	def avatar():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { avatar { url }}}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['avatar']['url']

	#get account firstname
	def firstname():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { firstName }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['firstName']

	#get account lastname
	def lastname():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { lastName }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['lastName']

	#get account username
	def username():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { username }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['username']

	#get account age
	def age():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { age }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['age']

	#get account birthdate
	def birthDate():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { birthday }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['birthday']

	#get account birthplace
	def birthPlace():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { placeOfBirth }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['placeOfBirth']

	#get account address
	def address():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { shippingAddress { fullAddress } }}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['profile']['shippingAddress']['fullAddress']

	#get account email
	def email():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { email }","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['email']

	#get account phone number
	def phone():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { phoneNumber }","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['phoneNumber']

	#get account type
	def type():

		payload = {
		    "query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { type }",
		    "variables": {},
		    "extensions": {}
		}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['type']


	#change account username
	def setUsername(new): #From their side, there's a bug who may make it not working

		payload = {"query":"mutation androidUpdateUsername($username: Username!) { updateUsername(input: {username: $username}) { errors { message path } }}","variables":{"username":"'+new+'"},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		return response.status_code

	#change account email
	def setEmail(new): #Working, but need a manual confirmation by mail.
		email = new
		payload = "{\"query\":\"mutation androidUpdateEmail($email: Email!) { updateEmail(input: {email: $email}) { errors { message path } }}\",\"variables\":{\"email\":\""+email+"\"},\"extensions\":{}}"

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		return response.status_code

	#change account phone
	def setPhone(new, code=CODE): #I dunno what API support, +33 6 00 00 00 00 format recommanded

		phone=new
		code=code
		payload = "{\"query\":\"mutation androidChangePhoneNumber($newPhoneNumber: PhoneNumber!, $passcode: Passcode!) { changePhoneNumber(input: {newPhoneNumber: $newPhoneNumber, passcode: $passcode}) { errors { message path } }}\",\"variables\":{\"passcode\":\""+code+"\",\"newPhoneNumber\":\""+phone+"\"},\"extensions\":{}}"

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		return response.status_code


	'''
		Get informations about Friends
	'''	
	class Friends:
		#get number of friends
		def howMany():
			payload = {"query":"query androidListFriendships { me { friendships { status user { __typename id } }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return len(data['data']['me']['friendships'])

		#get friends firstname
		def firstNames():
			payload = {"query":"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			friends = {}
			for friend in data['data']['me']['friendships']:
				friends[friend['user']['username']] = {"firstname": friend['user']['firstName'], "lastname": friend['user']['lastName'], "bankaccount": friend['user']['hasBankAccount']}

			friendsName = []
			for friend in friends:
				friendsName.append(friends[friend]['firstname'])

			return friendsName

		#get friends lastname
		def lastNames():
			payload = {"query":"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			friends = {}
			for friend in data['data']['me']['friendships']:
				friends[friend['user']['username']] = {"firstname": friend['user']['firstName'], "lastname": friend['user']['lastName'], "bankaccount": friend['user']['hasBankAccount']}

			friendsName = []
			for friend in friends:
				friendsName.append(friends[friend]['lastname'])

			return friendsName

		#get friends firstname with bank account
		def withBankAccounts():
			payload = {"query":"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			friends = {}
			for friend in data['data']['me']['friendships']:
				friends[friend['user']['username']] = {"firstname": friend['user']['firstName'], "lastname": friend['user']['lastName'], "bankaccount": friend['user']['hasBankAccount']}

			Friends = []
			for friend in friends:
				if friends[friend]['bankaccount']:
					Friends.append(friends[friend])

			return Friends


	'''
		Get informations about subscription plan
	'''
	class Subscription:
		#get account subscription status
		def status():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { id status } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['status']
	
		#get account subscription next billing date
		def nextBillingDate():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { id nextBilling { date } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['nextBilling']['date']
		
		#get account subscription next billing price
		def nextBillingPrice():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { ... Me_SubscriptionParts } }\n\nfragment Me_SubscriptionParts on Subscription { id nextBilling { amount { value currency { isoCode name symbol symbolFirst } } } plan { id price { value } }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['nextBilling']['amount']

		#get account subscription price
		def price():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { id plan { price { value }} } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['plan']['price']['value']

		#get account subscription name
		def name():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { id plan { name } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['plan']['name']


	'''
		Get account information (Parent)
	'''
	class Parent:
		#get parent id
		def id():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { id }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['id']

		#get parent firstname
		def firstname():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { firstName }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['firstName']

		#get parent lastname
		def lastname():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { lastName }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['lastName']

		#get parent username
		def username():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { username }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['username']

		#get parent email
		def email():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { email }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['email']

		#get parent phone number
		def phone():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { phoneNumber }}}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['phoneNumber']


	'''
		Get cards informations
	'''
	class Cards:
		#get cards
		def getAll():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts }}}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['cards']['nodes']

		#get card details
		def getDetails(cardId): #Not allowed while trying to get physical card details

			payload = {"query":"query androidUrlToGetPan($cardId: ID!) { urlToGetPan(cardId: $cardId) { url }}","variables": {"cardId": cardId},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			url = data['data']['urlToGetPan']['url']

			headers = {
			    'host': "virtualcard.bankable.cards",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+ TOKEN,
			    'accept-language': "en"
			}

			response = request("GET", url, headers=headers)			
			data = json.loads(response.text)

			num = data['card_pan']
			exp = data['card_exp_date']
			cvv = data['card_cvc2']

			return {"digits": num, "expiration": exp, "cvv": cvv}

		#get saved card for topup
		def getTopupCard():

			payload = {"query":"query androidListTopupCard { me { topupCards { ... Topup_TopupCardParts } }}\n\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			print(data)

			cards = []
			for card in data['data']['me']['topupCards']:
				cards.append({'id':card['id'], 'name': card['name'], 'expiration': card['expirationDate'], 'last4Digits': card['last4'], 'isDefault': card['default'], 'providSrcID': card['providerSourceId'], 'providPayID': card['providerPaymentId']})

			return cards 

		#get default card for paiement ID
		def defaultCardPaiementID():
			card = Account.Cards.getTopupCard()[0]

			return card['providSrcID']


		""" Cards action """
		#unblock card by ID
		def unblock(id):

			payload = {"query":"mutation androidUpdateCard($input: UpdateCardInput!) { updateCard(input: $input) { card { ... Card_CardParts } errors { path message} }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{"input":{"cardId": id,"attributes":{"blocked": "false"}}},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			return response.status_code

		#block card by ID
		def block(id):
			id=id
			payload = {"query":"mutation androidUpdateCard($input: UpdateCardInput!) { updateCard(input: $input) { card { ... Card_CardParts } errors { path message} }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{"input":{"cardId": id,"attributes":{"blocked": "true"}}},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			return response.status_code


		""" Physical card """
		#get physical card ID
		def physicalID():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id }\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "PhysicalCard":
					return card['id']

			raise Exception('No physical card found.') 


		""" Virtual card """
		#get virtual card ID
		def VirtualID():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id }\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					return card['id']

			raise Exception('No virtual card found.') 

		#get virtual card number
		def getVirtualCardNumber():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id }\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					card = Account.Cards.getDetails(Account.Cards.VirtualID())
					return card['digits']


			raise Exception('No virtual card found.') 
						
		#get virtual card expiration date
		def getVirtualCardExpiration():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id }\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					card = Account.Cards.getDetails(Account.Cards.VirtualID())
					return card['expiration']


			raise Exception('No virtual card found.') 
						
		#get virtual card cvv
		def getVirtualCardCVV():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id }\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					card = Account.Cards.getDetails(Account.Cards.VirtualID())
					return card['cvv']


			raise Exception('No virtual card found.') 
						

		""" Bank account """
		#get bank account id
		def getBankID():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { bankAccount { id }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['id']

		#get iban
		def getIban():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { bankAccount { iban }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['iban']

		#get bic
		def getBic():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { bankAccount { bic }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['bic']


	'''
		Get balance informations
	'''
	class Stats:

		#get recent transaction
		def recentTransactions(nb=20): #Default last 20 transactions

			howmany = nb
			payload = {"query":"query androidTransactions($first: Int, $after: String) { me { typedTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title status visibility amount { value currency { symbol } } category { name color image { url } } processedAt ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } typedFriendsTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title category { name image { url } } processedAt user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } }}\n\nfragment Vault_VaultMiniParts on Vault { name color emoji { name unicode }}","variables":{"numberOfComments":5,"first": howmany},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			recent = data['data']['me']['typedTransactions']['nodes']

			#for transa in recent:
			#	print(transa['title'], str(transa['amount']['value'])+str(transa['amount']['currency']['symbol']))

			return recent

		#get total number of transactions
		def totalTransactions():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { cardTransactionsCount }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['cardTransactionsCount']

		#getWeekStats ONLY EXPENSE, no stats for deposit displayed in API
		def week():

			limit, now = getLastWeek()
			user = Account.id()

			payload = {"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId": user,"to": now,"from": limit},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats

		#getMonthStats ONLY EXPENSE, no stats for deposit displayed in API
		def month():

			limit, now = getLastMonth()
			user = Account.id()
			
			payload = {"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":user,"to":now,"from":limit},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats

		#getYearStats ONLY EXPENSE, no stats for deposit displayed in API
		def year():

			limit, now = getLastYear()
			user = Account.id()
			
			payload = {"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":user,"to":now,"from":limit},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats

		#getAllStats ONLY EXPENSE, no stats for deposit displayed in API
		def all():

			limit, now = getTotal()
			user = Account.id()
			
			payload = {"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":user,"to":now,"from":limit},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats


	'''
		Informations about money
		Interaction with money
	'''
	class Money:
		#get balance
		def balance():

			payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { bankAccount { balance { value } }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['balance']['value']


		#Add money to account, with default card. Return 3Dsecure link to confirm
		def addFromSaved(cvv, amount, src):
			"""
				Return the 3D secure link
					-> Automate process: 
						hint: https://pypi.org/project/asms/ https://stackoverflow.com/a/39887459/11902707
								-- Add support to know the result (failed, canceled, success)
			"""
			payload = {"query":"mutation androidTopupAccount($paymentSource: PaymentSource!, $amount: AmountInput!, $cvv: Cvv!, $childId: ID, $recipientId: ID, $failureUrl: String, $successUrl: String) { topupAccount(input: { paymentSource: $paymentSource, cvv: $cvv, amount: $amount, childId: $childId, recipientId: $recipientId, failureUrl: $failureUrl, successUrl: $successUrl }) { paymentId secureFormUrl errors { message path } }}","variables":{"amount":{"value":amount,"currency":"EUR"},"paymentSource":src,"failureUrl":"https://eu.kard.app/3ds/failure","cvv":cvv,"successUrl":"https://eu.kard.app/3ds/success"},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			payID = data['data']['topupAccount']['paymentId']
			url = data['data']['topupAccount']['secureFormUrl']

			webbrowser.open(url, new=2)
			print("You now need to confirm 3D Secure code here:", url)
			return 

		#Send money to friend
		def send():
			raise Exception('Command not set. I need to get friends in Kard before lol')


	'''
		Use vaults
	'''
	class Vault:
		def __init__(self, name=""):
			self.name = name
		
		#Get vault ID
		def id(self):
			name = self.name

			payload = {"query":"query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\nfragment Vault_VaultParts on Vault { id name }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for vault in data["data"]["me"]["vaults"]:
				if vault["name"] == name:
					return vault["id"]

		#Get vault Emoji
		def emoji(self):
			name = self.name
			
			payload = {"query":"query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\nfragment Vault_VaultParts on Vault { id name emoji { name unicode }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for vault in data["data"]["me"]["vaults"]:
				if vault["name"] == name:
					return vault["emoji"]

		#Get vault Color
		def color(self):
			name = self.name
			
			payload = {"query":"query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\nfragment Vault_VaultParts on Vault { id name color }","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for vault in data["data"]["me"]["vaults"]:
				if vault["name"] == name:
					return vault["color"]

		#Get vault Goal
		def goal(self):
			name = self.name
		
			payload = {"query":"query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\nfragment Vault_VaultParts on Vault { id name goal { value }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for vault in data["data"]["me"]["vaults"]:
				if vault["name"] == name:
					return str(vault["goal"]['value']) + "€"

		#Get vault Balance
		def balance(self):
			name = self.name

			payload = {"query":"query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\nfragment Vault_VaultParts on Vault { id name balance { value }}","variables":{},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			for vault in data["data"]["me"]["vaults"]:
				if vault["name"] == name:
					return str(vault["balance"]["value"]) + "€"

		#This transfer money from balance to vault
		def topup(self, amount): #Amount of less than 1cents does not throw error, but nothing is done

			vault = self.id()
			amount=str(amount)

			payload = {"query":"mutation androidCreditVault($vaultId: ID!, $amount: AmountInput!) { creditVault(input: {vaultId: $vaultId, amount: $amount}) { errors { message path } }}","variables":{"amount":{"value": amount,"currency":"EUR"},"vaultId": vault},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			try:
				err = data['data']['creditVault']['errors'][0]['message']
			except:
				return response

			raise Exception(err)

		#Change vault color
		def changeColor(self, color):
			#Official colors. Any (maybe not) HTML color code work :D
			colors = {"black":"#1b1d20", "green":"#3ce977",
						"purpleblack": "#1f193f", "grey":"#75818c",
							"pink":"#f943b1", "yellow":"#ffca10",
								"orange":"#ff9455", "red": "#ff5f7c",
									"cyan":"#15e4da", "blue": "#35c4ff",
										"purpledark": "#9850ff", "purplelight": "#bd3fdd"
					}

			vault = self.id()
			color=color

			payload = {"query":"mutation androidUpdateVault($vaultId: ID!, $color: HexadecimalColorCode, $emoji: EmojiInput, $name: Name) { updateVault(input: {vaultId: $vaultId, color: $color, emoji: $emoji, name: $name}) { errors { message path } }}","variables":{"vaultId":vault,"color":color},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			
			try:
				err = data['errors']
			except:
				return response

			raise Exception(err[0]['extensions']['problems'][0]['explanation'])

		#Change vault icon
		def changeEmote(self, emote):
			emotes = ["🎁", "🎈", "🛍", "💰", "😈", "🎓", "🏝", "🎫", "🎸", "✈️", "👟", "📱", "🎮", "🛴", "🛵"] #If emote not in list, a default emote is set (bank building)

			emote=emote
			vault = self.id()

			payload = {"query":"mutation androidUpdateVault($vaultId: ID!, $color: HexadecimalColorCode, $emoji: EmojiInput, $name: Name) { updateVault(input: {vaultId: $vaultId, color: $color, emoji: $emoji, name: $name}) { errors { message path } }}","variables":{"vaultId":vault,"emoji":emote},"extensions":{}}

			response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)
			data = json.loads(response.text)
			
			try:
				err = data['errors']
			except:
				return response

			raise Exception(err[0]['extensions']['problems'][0]['explanation'])


		#create a vault
		def create(self, goal): #Appear to be bug with round amount (1000, 2000, ...), one or two 0 are removed but 99999 work fine

			name=self.name
			goal=str(goal)

			payload = {"query":"mutation androidCreateVault($goal: AmountInput!, $name: Name!) { createVault(input: {goal: $goal, name: $name}) { errors { message path } vault { id } }}","variables":{"goal":{"value":goal,"currency":"EUR"},"name":name},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			return response

		#empty a vault
		def empty(self):
			id = self.id()

			if id is None:
				raise Exception('There is no Vault named "'+ self.name + '" !')

			payload = {"query":"mutation androidCloseVault($vaultId: ID!) { closeVault(input: {vaultId: $vaultId}) { errors { message path } }}","variables":{"vaultId":id},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)
			return response


	'''
		Transactions data
	'''
	class Transaction():
		def __init(self, id):
			self.id = id

		#change transaction name
		def setName(self, name):

			id = self.id

			payload = {"query":"mutation androidUpdateTransaction($input: UpdateTransactionInput!, $numberOfComments: Int) { updateTransaction(input: $input) { errors { message path } transaction { ... Transaction_TransactionParts } }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\n\nfragment Vault_VaultParts on Vault { id name color emoji { name unicode } goal { value } balance { value }}\n\nfragment Transaction_TransactionParts on Transaction { __typename id title status image { id url } visibility amount { value currency { symbol } } category { name color image { url } } processedAt reactions { totalQuantity emoji { name unicode } paginatedDetails { nodes { quantity emoji { name unicode } user { id firstName lastName username avatar { url } } } } } userReactions { totalQuantity emoji { name unicode } paginatedDetails { nodes { emoji { name unicode } id } } } comments(first: $numberOfComments) { totalCount pageInfo { endCursor hasNextPage } nodes { id comment createdAt user { id firstName lastName avatar { url } } } } user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on CardTransaction { card { ... Card_CardParts } } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultParts } } ... on MoneyLinkTransaction { from message }}","variables":{"numberOfComments":5,"input":{"transactionId": id,"attributes":{"title": name}}},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			return response.status_code

		#add comment on transaction
		def addComment(self, comment):
			
			id = self.id

			payload = {"query":"mutation androidAddComment($commentableId: ID!, $comment: String!) { addComment(input: { commentableId: $commentableId, comment: $comment }) { errors { message path } comment { id createdAt comment user { id firstName lastName avatar { url } } } }}","variables":{"commentableId": id,"comment": comment},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			if response.status_code == 200:
				return response.status_code
			else:
				print(response.text)
				raise Exception('Response status code invalid: '+ str(response.status_code))

		#del comment on transaction
		def delComment(self):
			id = self.id

			payload = {"query":"mutation androidDeleteComment($commentId: ID!) { deleteComment(input: { commentId: $commentId}) { errors { message path } }}","variables":{"commentId":id},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			if response.status_code == 200:
				return response.status_code
			else:
				print(response.text)
				raise Exception('Response status code invalid: '+ str(response.status_code))


		#get last transaction
		def last_get(self):

			payload = {"query":"query androidTransactions($first: Int, $after: String) { me { bankAccount { balance { value } } typedTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title status visibility amount { value currency { symbol } } category { name color image { url } } processedAt ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } typedFriendsTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title category { name image { url } } processedAt user { id firstName lastName username avatar { url } }","variables":{"numberOfComments":5,"first":20},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['me']['typedTransactions']['nodes'][0]

		#get last transaction id
		def last_getID(self):

			data = last_get()
			return data['id']


		#get number of comment on transaction
		def getNumberOfComments(self):
			id = self.id

			payload = {"query":"query androidTransaction($id: ID!, $numberOfComments: Int) { transaction(transactionId: $id) { ... Transaction_TransactionParts }}\n\nfragment Transaction_TransactionParts on Transaction {comments(first: $numberOfComments) { totalCount }}","variables":{"numberOfComments":5,"id":id},"extensions":{}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['transaction']['comments']['totalCount']

		#get last transaction comments
		def last_getComments(self):
			id = last_getID()

			payload = {"query":"query androidTransaction($id: ID!) { transaction(transactionId: $id) { ... Transaction_TransactionParts }}\n\nfragment Transaction_TransactionParts on Transaction { comments { nodes { id comment createdAt user { id firstName lastName avatar { url }}}}}", "variables": {"numberOfComments": 5, "id":id}, "extensions": {}}

			response = request("POST", API_URL, json=payload, headers=HEADERS)
			data = json.loads(response.text)

			return data['data']['transaction']['comments']['nodes']

		#get last transaction last comment
		def last_getLastComment(self):
			lastComment = last_getComments()[0]

			return lastComment

		#get last transaction last comment ID
		def last_getLastCommentID(self):
			comment = last_getLastComment()

			return comment['id']

	'''
		Random account informations
	'''
	#get account mail status (verified or not)
	def isEmailConfirmed():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\n\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\n\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\n\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\n\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\n\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\n\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['emailConfirmed']

	#get slash link
	def slashLink(amount=""):
		username = Account.username()
		amount = str(amount)

		return 'https://s.kard.eu/'+username+'/'+amount

	#get account referral code
	def referralCode():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\n\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\n\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\n\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\n\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\n\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\n\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['referralCode']

	#get account referral link
	def referralLink():

		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\n\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\n\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\n\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\n\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\n\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\n\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}","variables":{},"extensions":{}}

		response = request("POST", API_URL, json=payload, headers=HEADERS)
		data = json.loads(response.text)

		return data['data']['me']['referralUrl']

