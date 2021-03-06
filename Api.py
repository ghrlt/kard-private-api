import requests, json, time, datetime
import webbrowser


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
		if int(m)%2 == 0 and not m == "02":
			d = "31"
		else:
			d = "30"
		m = "0"+str(int(m)-1)

	lastWeek = y+"-"+m+"-"+d

	return lastWeek, today

def getLastMonth():
	today = datetime.date.today()

	y = str(today).split('-')[0]
	m = str(today).split('-')[1]
	d = "01"

	lastMonth = y+"-"+m+"-"+d

	return lastMonth, today

def getLastYear():
	today = datetime.date.today()

	y = str(today).split('-')[0]
	m = "01"
	d = "01"

	lastYear = y+"-"+m+"-"+d

	return lastYear, today

def getTotal():
	today = datetime.date.today()

	beginning = Account().CreationDate()
	beginning = str(beginning.split("T")[0])

	return str(beginning), str(today)


global TOKEN
TOKEN = readF('config')['login']['token']
VENDORIDENTIFIER = readF('config')['login']['identifier']
USERAGENT = "Gaetan/911"

NUM = readF('config')['login']['phone']
CODE = readF('config')['login']['code']

#Login
def login(num=NUM, code=CODE):

	num=num #Like this "06 00 00 00 00"
	code=code


	#Request OTP
	url = "https://api.kard.eu/graphql"

	payload = "{\"query\":\"mutation androidInitSession($createUser: Boolean, $phoneNumber: PhoneNumber!, $platform: DevicePlatform, $vendorIdentifier: String!) { initSession(input: {createUser: $createUser, phoneNumber: $phoneNumber, platform: $platform, vendorIdentifier: $vendorIdentifier}) { challenge expiresAt errors { path message } }}\",\"variables\":{\"platform\":\"ANDROID\",\"createUser\":true,\"phoneNumber\":\""+num+"\",\"vendorIdentifier\":\""+VENDORIDENTIFIER+"\"},\"extensions\":{}}"
	headers = {
	    'content-type': "application/json",
	    'content-length': "492",
	    'host': "api.kard.eu",
	    'connection': "Keep-Alive",
	    'accept-encoding': "gzip",
	    'user-agent': USERAGENT,
	    'vendoridentifier': VENDORIDENTIFIER,
	    'accept-language': "en"
	}

	response = requests.request("POST", url, data=payload, headers=headers)
	data = json.loads(response.text)
	try:
		err = data['errors']['extensions']['problems']['explanation']
		raise Exception(err)
	except:
		if data['data']['initSession']['challenge'] == "OTP":
			otp = input("You need to confirm OTP code sent to " + num + " : ")

			payload = "{'query':'mutation androidVerifyOTP($authenticationProvider: AuthenticationProviderInput, $code: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { verifyOtp(input: {authenticationProvider: $authenticationProvider, code: $code, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { challenge accessToken refreshToken errors { path message } }}','variables':{'phoneNumber':'"+num+"','vendorIdentifier':'"+VENDORIDENTIFIER+"','code':''"+otp+"''},'extensions':{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "517",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'accept-language': "en"
			}

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

		#else:
		#	raise Exception(data['data']['verifyOtp']['errors']['message'])	

		elif data['data']['initSession']['challenge'] == "PASSCODE":
			pass
		else:
			print('˄˄˄')
			print(data)
			print('˅˅˅')
			raise Exception('Never saw this. Open an issue with all text before please.')

		try:
			passcode = data['data']['verifyOtp']['challenge']
		except: 
			pass

		global TOKEN
		payload = "{\"query\":\"mutation androidSignIn($authenticationProvider: AuthenticationProviderInput,$passcode: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { signIn(input: {authenticationProvider: $authenticationProvider,passcode: $passcode, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { accessToken refreshToken errors { path message } }}\",\"variables\":{\"passcode\":\""+code+"\",\"phoneNumber\":\""+num+"\",\"vendorIdentifier\":\""+VENDORIDENTIFIER+"\"},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "513",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
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
	def CreationDate():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { createdAt }","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "126",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['createdAt'] #Formatting?

	#get account id
	def ID():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { id }","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "119",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['id']

	#get account avatar
	def Avatar():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { avatar { url }}}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "141",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['avatar']['url']

	#get account firstname
	def Firstname():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { firstName }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "137",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['firstName']

	#get account lastname
	def Lastname():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { lastName }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "136",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['lastName']

	#get account username
	def Username():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { username }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "136",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['username']

	#get account age
	def Age():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { age }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "131",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['age']

	#get account birthdate
	def BirthDate():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { birthday }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "135",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['birthday']

	#get account birthplace
	def BirthPlace():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { placeOfBirth }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "2920",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['placeOfBirth']

	#get account address
	def Address():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { shippingAddress { fullAddress } }}","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "159",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['profile']['shippingAddress']['fullAddress']

	#get account email
	def Email():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { email }","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "122",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['email']

	#get account phone number
	def Phone():

		url = "https://api.kard.eu/graphql"

		payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { phoneNumber }","variables":{},"extensions":{}}'
		headers = {
		    'content-type': "application/json",
		    'content-length': "128",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['phoneNumber']

	#get account type
	def Type():

		url = "https://api.kard.eu/graphql"

		payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "2920",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['type']

	#change account email
	def setEmail(new): #Working, but need a manual confirmation by mail.
		email = new
		url = "https://api.kard.eu/graphql"

		payload = "{\"query\":\"mutation androidUpdateEmail($email: Email!) { updateEmail(input: {email: $email}) { errors { message path } }}\",\"variables\":{\"email\":\""+email+"\"},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "184",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		return response.status_code

	#change account phone number
	def setPhone(new, code): #I dunno what API support, +33 6 00 00 00 00 format recommanded

		phone=new
		code=code
		url = "https://api.kard.eu/graphql"

		payload = "{\"query\":\"mutation androidChangePhoneNumber($newPhoneNumber: PhoneNumber!, $passcode: Passcode!) { changePhoneNumber(input: {newPhoneNumber: $newPhoneNumber, passcode: $passcode}) { errors { message path } }}\",\"variables\":{\"passcode\":\""+code+"\",\"newPhoneNumber\":\""+phone+"\"},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "295",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		return response.status_code

	#change account profile pic
	def setPic(img):
		img = ""

		url = "https://api.kard.eu/graphql"

		headers = {
		    'content-type': "multipart/form-data; boundary=88ca1728-e2d3-4766-9346-1d0a9b31ab56",
		    'content-length': "70385",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ2MTc2MDYsImV4cCI6MTYxNTIyMjQwNn0.z4cg1gxH1IsbsAhwQB4I1hjIDanTvnuW4p1ezauYwfA",
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)

		print(response.text)


	
	class Friends:
		#get number of friends
		def howMany():
			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "282",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return len(data['data']['me']['friendships'])

		#get friends firstname
		def firstNames():
			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "282",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
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
			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "282",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
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
			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidListFriendships { me { friendships { status user { __typename avatar { url } id firstName lastName username hasBankAccount } } contacts { identifier status user { __typename avatar { url } id firstName lastName username } } }}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "282",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			friends = {}
			for friend in data['data']['me']['friendships']:
				friends[friend['user']['username']] = {"firstname": friend['user']['firstName'], "lastname": friend['user']['lastName'], "bankaccount": friend['user']['hasBankAccount']}

			friends = []
			for friend in friends:
				if friends[friend]['bankaccount']:
					friends.append(friends[friend])

			return friends



	'''
		Get informations about subscription plan
	'''
	class Subscription:
		#get account subscription status
		def Status():

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "2920",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['status']
	
		#get account subscription next billing date
		def NextBillingDate():

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "2920",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['nextBilling']['date']
		
		#get account subscription next billing price
		def getAccountNextBillingPrice():

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "2920",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['nextBilling']['amount']

		#get account subscription price
		def getAccountSubscriptionPrice():

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "2920",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['plan']['price']['value']

		#get account subscription name
		def getAccountSubscriptionName():

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "2920",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ1NTkxMjAsImV4cCI6MTYxNTE2MzkyMH0.cpQLZxONgNp2pyrLUMSGOvmzAIf6p6p38mevsDrUJvw",
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['subscription']['plan']['name']


	'''
		Get account information (Parent)
	'''
	class Parent:
		#get parent id
		def getParentID():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { id }}}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "144",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['id']

		#get parent firstname
		def getParentFirstname():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { firstName }}}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "151",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['firstName']

		#get parent lastname
		def getParentLastname():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { lastName }}}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "150",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['lastName']

		#get parent username
		def getParentUsername():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { username }}}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "150",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['username']

		#get parent email
		def getParentEmail():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { email }}}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "147",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['email']

		#get parent phone number
		def getParentPhone():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { parent { status user { phoneNumber }}}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "153",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['parent']['user']['phoneNumber']


	'''
		Get cards informations
	'''
	class Cards:
		#get cards
		def getCards():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts }}}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "152",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['cards']['nodes']

		#get card details
		def getCardDetails(id): #Not allowed while trying to get physical card details
			id=id

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidUrlToGetPan($cardId: ID!) { urlToGetPan(cardId: $cardId) { id url }}\",\"variables\":{\"cardId\":\""+id+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "210",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)
			url = data['data']['urlToGetPan']['url']
			
			headers = {
			    'host': "virtualcard.bankable.cards",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("GET", url, headers=headers)
			data = json.loads(response.text)

			num = data['card_pan']
			exp = data['card_exp_date']
			cvv = data['card_cvc2']

			return {"digits": num, "expiration": exp, "cvv": cvv}

		#get saved card for topup
		def getTopupCard():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidListTopupCard { me { topupCards { ... Topup_TopupCardParts } }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "240",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			cards = {}
			for card in data['data']['me']['topupCards']:
				cards = {'id':card['id'], 'name': card['name'], 'expiration': card['expirationDate'], 'last4Digits': card['last4'], 'isDefault': card['default'], 'providSrcID': card['providerSourceId'], 'providPayID': card['providerPaymentId']}

			return cards 


		""" Cards action """
		#unblock card by ID
		def unblockCard(id):

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"mutation androidUpdateCard($input: UpdateCardInput!) { updateCard(input: $input) { card { ... Card_CardParts } errors { path message} }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{"input":{"cardId":""+id+"","attributes":{"blocked":false}}},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "468",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			return response.status_code

		#block card by ID
		def blockCard(id):
			id=id
			url = "https://api.kard.eu/graphql"

			payload = '{"query":"mutation androidUpdateCard($input: UpdateCardInput!) { updateCard(input: $input) { card { ... Card_CardParts } errors { path message} }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{"input":{"cardId":""+id+"","attributes":{"blocked":true}}},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "467",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			return response.status_code


		""" Physical card """
		#get physical card ID
		def getPhysicalCardID():

			url = "https://api.kard.eu/graphql"


			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id }\\n\\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "212",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "PhysicalCard":
					return card['id']

			raise Exception('No physical card found.') 


		""" Virtual card """
		#get virtual card ID
		def VirtualID():

			url = "https://api.kard.eu/graphql"


			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id }\\n\\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "212",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					return card['id']

			raise Exception('No virtual card found.') 

		#get virtual card number
		def getVirtualCardNumber():


			url = "https://api.kard.eu/graphql"


			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id }\\n\\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "212",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					card = getCardDetails(self.VirtualID())
					return card['digits']


			raise Exception('No virtual card found.') 
						
		#get virtual card expiration date
		def getVirtualCardExpiration():

			url = "https://api.kard.eu/graphql"


			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id }\\n\\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "212",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					card = getCardDetails(self.VirtualID())
					return card['expiration']


			raise Exception('No virtual card found.') 
						
		#get virtual card cvv
		def getVirtualCardCVV():

			url = "https://api.kard.eu/graphql"


			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id }\\n\\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts } } }","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "2920",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			for card in data['data']['me']['cards']['nodes']:
				if card['__typename'] == "VirtualCard":
					card = getCardDetails(self.VirtualID())
					return card['cvv']


			raise Exception('No virtual card found.') 
						

		""" Bank account """
		#get bank account id
		def getBankID():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Me_MeParts on Me { bankAccount { id }}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "136",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['id']

		#get iban
		def getIban():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Me_MeParts on Me { bankAccount { iban }}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "138",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['iban']

		#get bic
		def getBic():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Me_MeParts on Me { bankAccount { bic }}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "137",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['bic']


	'''
		Get balance informations
	'''
	class Stats:

		#get recent transaction
		def RecentTransactions(): #Need to know how many? since when?

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransactions($first: Int, $after: String) { me { typedTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title status visibility amount { value currency { symbol } } category { name color image { url } } processedAt ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } typedFriendsTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title category { name image { url } } processedAt user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } }}\\n\\nfragment Vault_VaultMiniParts on Vault { name color emoji { name unicode }}","variables":{"numberOfComments":5,"first":20},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "1258",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)
			recent = data['data']['me']['typedTransactions']['nodes']

			#for transa in recent:
			#	print(transa['title'], str(transa['amount']['value'])+str(transa['amount']['currency']['symbol']))

			return recent

		#get total number of transactions
		def TotalTransactions():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Me_MeParts on Me { cardTransactionsCount }","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "140",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['cardTransactionsCount']

		#getWeekStats ONLY EXPENSE, no stats for deposit displayed in API
		def Week():

			limit, now = getLastWeek()
			user = Account().ID()

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":"'+user+'","to":"'+now+'","from":"'+limit+'"},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "376",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats

		#getMonthStats ONLY EXPENSE, no stats for deposit displayed in API
		def Month():

			limit, now = getLastMonth()
			user = Account().ID()
			
			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":"'+user+'","to":"'+now+'","from":"'+limit+'"},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "376",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats

		#getYearStats ONLY EXPENSE, no stats for deposit displayed in API
		def Year():

			limit, now = getLastYear()
			user = Account().ID()
			
			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":"'+user+'","to":"'+now+'","from":"'+limit+'"},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "376",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			stats = {}
			total = 0
			for category in data['data']['transactionsByCategoryOverview']:
				stats[category['category']['name']] = {"amount": category['amount']['value'], "percent": category['percentage'], "nbTransa": category['count']}
				total += category['amount']['value']
			
			stats['total'] = abs(total)

			return stats

		#getAllStats ONLY EXPENSE, no stats for deposit displayed in API
		def All():

			limit, now = getTotal()
			user = Account().ID()
			
			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransactionsByCategoryOverview($userId: ID!, $from: ISO8601DateStrict!, $to: ISO8601DateStrict!) { transactionsByCategoryOverview(userId: $userId, from: $from,to: $to) { category { id name color image { url } } amount { value currency { symbol } } count percentage }}","variables":{"userId":"'+user+'","to":"'+now+'","from":"'+limit+'"},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "376",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
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
		def Balance():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Me_MeParts on Me { bankAccount { balance { value } }}","variables":{},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "151",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['bankAccount']['balance']['value']

		#get default card for paiement ID
		def DefaultCardPaiementID():
			card = getTopupCard()

			return card['providSrcID']

		#Add money to account, with default card. Return 3Dsecure link to confirm
		def add(cvv, amount, src):
			"""
				Return the 3D secure link
					-> Automate process: 
						hint: https://pypi.org/project/asms/ https://stackoverflow.com/a/39887459/11902707
								-- Add support to know the result (failed, canceled, success)
			"""

			cvv=cvv
			amount=amount
			src=src

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidTopupAccount($paymentSource: PaymentSource!, $amount: AmountInput!, $cvv: Cvv!, $childId: ID, $recipientId: ID, $failureUrl: String, $successUrl: String) { topupAccount(input: { paymentSource: $paymentSource, cvv: $cvv, amount: $amount, childId: $childId, recipientId: $recipientId, failureUrl: $failureUrl, successUrl: $successUrl }) { paymentId secureFormUrl errors { message path } }}\",\"variables\":{\"amount\":{\"value\":"+amount+",\"currency\":\"EUR\"},\"paymentSource\":\""+src+"\",\"failureUrl\":\"https://eu.kard.app/3ds/failure\",\"cvv\":\""+cvv+"\",\"successUrl\":\"https://eu.kard.app/3ds/success\"},\"extensions\":{}}"
			headers = {
			'content-type': "application/json",
			'content-length': "640",
			'host': "api.kard.eu",
			'connection': "Keep-Alive",
			'accept-encoding': "gzip",
			'user-agent': USERAGENT,
			'vendoridentifier': VENDORIDENTIFIER,
			'authorization': "Bearer "+TOKEN,
			'accept-language': "en"
			}

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			payID = data['data']['topupAccount']['paymentId']
			url = data['data']['topupAccount']['secureFormUrl']

			webbrowser.open(url, new=2)
			return# url



	'''
		Use vaults
	'''
	class Vault:
		#Get vault ID		If name==all, return all vaults ; if name = VaultName, return the id for it
		def ID(name):
			name=name

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidListVault { me { vaults { ... Vault_VaultParts } }}\\n\\nfragment Vault_VaultParts on Vault { id name }\",\"variables\":{},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "218",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)

			data = json.loads(response.text)

			if name == "all":
				ids = []
				for vault in data["data"]["me"]["vaults"]:
					ids.append(vault["id"])

				return ids

			else:
				for vault in data["data"]["me"]["vaults"]:
					if vault["name"] == name:
						return vault["id"]
		#Get vault Emoji	If name==all, return all vaults ; if name = VaultName, return the id for it
		def Emoji(name):
			#To do
			#payload = "{\"query\":\"query androidListVault { me { vaults { ... Vault_VaultParts } }}\\n\\nfragment Vault_VaultParts on Vault { id name emoji { name unicode }}\",\"variables\":{},\"extensions\":{}}"
			pass
		#Get vault Color	If name==all, return all vaults ; if name = VaultName, return the id for it
		def Color(name):
			#To do
			#payload = "{\"query\":\"query androidListVault { me { vaults { ... Vault_VaultParts } }}\\n\\nfragment Vault_VaultParts on Vault { id name color }\",\"variables\":{},\"extensions\":{}}"
			pass
		#Get vault Goal		If name==all, return all vaults ; if name = VaultName, return the id for it
		def Goal(name):
			#To do
			#payload = "{\"query\":\"query androidListVault { me { vaults { ... Vault_VaultParts } }}\\n\\nfragment Vault_VaultParts on Vault { id name goal { value }}\",\"variables\":{},\"extensions\":{}}"
			pass
		#Get vault Balance	If name==all, return all vaults ; if name = VaultName, return the id for it
		def Balance(name):
			#To do
			#payload = "{\"query\":\"query androidListVault { me { vaults { ... Vault_VaultParts } }}\\n\\nfragment Vault_VaultParts on Vault { id name balance { value }}\",\"variables\":{},\"extensions\":{}}"
			pass

		#This transfer money from balance to vault
		def Topup(vault, amount):

			vault=vault
			amount=amount

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidCreditVault($vaultId: ID!, $amount: AmountInput!) { creditVault(input: {vaultId: $vaultId, amount: $amount}) { errors { message path } }}\",\"variables\":{\"amount\":{\"value\":"+amount+",\"currency\":\"EUR\"},\"vaultId\":\""+vault+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "334",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)

			print(response.text)

		#Change vault color
		def ChangeColor(vault, color):
			#Official colors. Any HTML color code work :D
			colors = {"black":"#1b1d20", "green":"#3ce977",
						"purpleblack": "#1f193f", "grey":"#75818c",
							"pink":"#f943b1", "yellow":"#ffca10",
								"orange":"#ff9455", "red": "#ff5f7c",
									"cyan":"#15e4da", "blue": "#35c4ff",
										"purpledark": "#9850ff", "purplelight": "#bd3fdd"
					}

			vault=vault
			color=color

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidUpdateVault($vaultId: ID!, $color: HexadecimalColorCode, $emoji: EmojiInput, $name: Name) { updateVault(input: {vaultId: $vaultId, color: $color, emoji: $emoji, name: $name}) { errors { message path } }}\",\"variables\":{\"vaultId\":\""+vault+"\",\"color\":\""+color+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "378",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)

			print(response.text)

		#Change vault icon
		def ChangeEmote(vault, emote):
			emotes = ["🎁", "🎈", "🛍", "💰", "😈", "🎓", "🏝", "🎫", "🎸", "✈️", "👟", "📱", "🎮", "🛴", "🛵"] #If emote not in list, default emote is set (bank building)

			emote=emote
			vault=vault

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidUpdateVault($vaultId: ID!, $color: HexadecimalColorCode, $emoji: EmojiInput, $name: Name) { updateVault(input: {vaultId: $vaultId, color: $color, emoji: $emoji, name: $name}) { errors { message path } }}\",\"variables\":{\"vaultId\":\""+vault+"\",\"emoji\":\""+emote+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "375",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)

			print(response.text)

		#create a vault
		def Create(name, goal):

			name=name
			goal=goal

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidCreateVault($goal: AmountInput!, $name: Name!) { createVault(input: {goal: $goal, name: $name}) { errors { message path } vault { id } }}\",\"variables\":{\"goal\":{\"value\":"+goal+",\"currency\":\"EUR\"},\"name\":\""+name+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "250",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)

		#empty a vault
		def Empty(id):
			id=id

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidCloseVault($vaultId: ID!) { closeVault(input: {vaultId: $vaultId}) { errors { message path } }}\",\"variables\":{\"vaultId\":\""+id+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "252",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)

			print(response.text)


	'''
		Transactions data
	'''
	class Transaction():
		def __init(self, id):
			self.id = id

		#change transaction name
		def setName(name):

			id = self.id

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidUpdateTransaction($input: UpdateTransactionInput!, $numberOfComments: Int) { updateTransaction(input: $input) { errors { message path } transaction { ... Transaction_TransactionParts } }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Vault_VaultParts on Vault { id name color emoji { name unicode } goal { value } balance { value }}\\n\\nfragment Transaction_TransactionParts on Transaction { __typename id title status image { id url } visibility amount { value currency { symbol } } category { name color image { url } } processedAt reactions { totalQuantity emoji { name unicode } paginatedDetails { nodes { quantity emoji { name unicode } user { id firstName lastName username avatar { url } } } } } userReactions { totalQuantity emoji { name unicode } paginatedDetails { nodes { emoji { name unicode } id } } } comments(first: $numberOfComments) { totalCount pageInfo { endCursor hasNextPage } nodes { id comment createdAt user { id firstName lastName avatar { url } } } } user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on CardTransaction { card { ... Card_CardParts } } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultParts } } ... on MoneyLinkTransaction { from message }}\",\"variables\":{\"numberOfComments\":5,\"input\":{\"transactionId\":\""+id+"\",\"attributes\":{\"title\":\""+name+"\"}}},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "1730",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			return response.status_code

		#add comment on transaction
		def addComment(comment):
			
			id = self.id
			comment=comment

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidAddComment($commentableId: ID!, $comment: String!) { addComment(input: { commentableId: $commentableId, comment: $comment }) { errors { message path } comment { id createdAt comment user { id firstName lastName avatar { url } } } }}\",\"variables\":{\"commentableId\":\""+id+"\",\"comment\":\""+comment+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "416",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			if response.status_code == 200:
				return response.status_code
			else:
				print(response.text)
				raise Exception('Response status code invalid: '+ str(response.status_code))

		#del comment on transaction
		def delComment():
			id = self.id

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"mutation androidDeleteComment($commentId: ID!) { deleteComment(input: { commentId: $commentId}) { errors { message path } }}\",\"variables\":{\"commentId\":\""+id+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "280",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			if response.status_code == 200:
				return response.status_code
			else:
				print(response.text)
				raise Exception('Response status code invalid: '+ str(response.status_code))


		#get last transaction
		def Last_get():

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransactions($first: Int, $after: String) { me { bankAccount { balance { value } } typedTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title status visibility amount { value currency { symbol } } category { name color image { url } } processedAt ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } typedFriendsTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title category { name image { url } } processedAt user { id firstName lastName username avatar { url } }","variables":{"numberOfComments":5,"first":20},"extensions":{}}'
			headers = {
			    'content-type': "application/json",
			    'content-length': "1290",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['me']['typedTransactions']['nodes'][0]

		#get last transaction id
		def Last_getID():

			data = getLatest()
			return data['id']


		#get number of comment on transaction
		def getNumberOfComments():
			id = self.id

			url = "https://api.kard.eu/graphql"

			payload = "{\"query\":\"query androidTransaction($id: ID!, $numberOfComments: Int) { transaction(transactionId: $id) { ... Transaction_TransactionParts }}\\n\\nfragment Transaction_TransactionParts on Transaction {comments(first: $numberOfComments) { totalCount }}\",\"variables\":{\"numberOfComments\":5,\"id\":\""+id+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "1606",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['transaction']['comments']['totalCount']

		#get last transaction comments
		def Last_getComments():
			id = Last_getID()

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"query androidTransaction($id: ID!) { transaction(transactionId: $id) { ... Transaction_TransactionParts }}\n\nfragment Transaction_TransactionParts on Transaction { comments { nodes { id comment createdAt user { id firstName lastName avatar { url }}}}}", "variables": {"numberOfComments": 5, "id":"'+id+'"}, "extensions": {}}'
			#payload = "{\"query\":\"query androidTransaction($id: ID!, $numberOfComments: Int) { transaction(transactionId: $id) { ... Transaction_TransactionParts }}\\n\\nfragment Transaction_TransactionParts on Transaction comments(first: $numberOfComments) { nodes { id comment createdAt user { id firstName lastName avatar { url } } } } user { id firstName lastName username avatar { url } }}\",\"variables\":{\"numberOfComments\":5,\"id\":\""+id+"\"},\"extensions\":{}}"
			headers = {
			    'content-type': "application/json",
			    'content-length': "1606",
			    'host': "api.kard.eu",
			    'connection': "Keep-Alive",
			    'accept-encoding': "gzip",
			    'user-agent': USERAGENT,
			    'vendoridentifier': VENDORIDENTIFIER,
			    'authorization': "Bearer "+TOKEN,
			    'accept-language': "en"
			    }

			response = requests.request("POST", url, data=payload, headers=headers)
			data = json.loads(response.text)

			return data['data']['transaction']['comments']['nodes']

		#get last transaction last comment
		def Last_getLastComment():
			lastComment = Last_getComments()[0]

			return lastComment

		#get last transaction last comment ID
		def Last_getLastCommentID():
			comment = Last_getLastComment()

			return comment['id']

	'''
		Random account informations
	'''
	#get account mail status (verified or not)
	def isEmailConfirmed():

		url = "https://api.kard.eu/graphql"

		payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "2920",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['emailConfirmed']

	#get slash link
	def SlashLink(amount=""):
		username = getAccountUsername()
		amount = str(amount)

		return 'https://s.kard.eu/'+username+'/'+amount

	#get account referral code
	def ReferalCode():

		url = "https://api.kard.eu/graphql"

		payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "2920",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['referralCode']

	#get account referral link
	def ReferralLink():

		url = "https://api.kard.eu/graphql"

		payload = "{\"query\":\"query androidMe { me { ... Me_MeParts }}\\n\\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}\\n\\nfragment Topup_TopupCardParts on TopupCard { id name expirationDate default last4 providerSourceId providerPaymentId}\\n\\nfragment Me_KycParts on Kyc { required deadline globalStatus fundsOrigin { status value } identityVerification { status url } proofOfAddress { status files { contentType url ... on Image { width height } } }}\\n\\nfragment Topup_RecurringParts on RecurringPayment { id active amount { value currency { symbol isoCode } } child { id } firstPayment nextPayment cancelledAt topupCard { ... Topup_TopupCardParts }}\\n\\nfragment Me_SubscriptionParts on Subscription { id status cancelledAt cancellationReason nextBilling { date amount { value currency { isoCode name symbol symbolFirst } } } plan { __typename id periodUnit name price { value } }}\\n\\nfragment Me_TopupRequestParts on TopupRequest { id amount { value currency { symbol isoCode } } reason accepted cancelled declined requester { id firstName lastName avatar { url } }}\\n\\nfragment Me_MeParts on Me { id type profile { avatar { url } firstName lastName username age birthday placeOfBirth shippingAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } homeAddress { firstName lastName street line1 line2 zipcode city state country fullAddress } } email emailConfirmed unconfirmedEmail phoneNumber referralCode referralUrl bankAccount { id iban bic user { firstName lastName } balance { value currency { symbol isoCode } } } card { id } cardBeingSetup { __typename id customText name ... on PhysicalCard { design } } cards { nodes { ... Card_CardParts } } earnings { value currency { symbol isoCode } } onboardingDone pendingDebts { amount { value currency { symbol isoCode } } id owner { avatar { url } firstName id lastName username } reason } topupCards { ... Topup_TopupCardParts } kyc { ... Me_KycParts } parent { status user { id firstName lastName username email phoneNumber claimId hasTopupCard } } children { id status user { id email phoneNumber profile { firstName lastName username avatar {url} birthday } kyc { ... Me_KycParts } cardBeingSetup { ... Card_CardParts } cards { nodes { ... Card_CardParts } } bankAccount { balance { value currency { symbol isoCode } } } incomingRecurringPayment { ... Topup_RecurringParts } savingsAmount { value } } } subscription { ... Me_SubscriptionParts } outgoingRecurringPayments { ... Topup_RecurringParts } incomingRecurringPayment { ... Topup_RecurringParts } fundsOrigin canOrderCard externalAuthenticationProviders { id type uniqueId } claimId cardTransactionsCount topupRequestsFromChildren { ... Me_TopupRequestParts } topupRequestsToParent { ... Me_TopupRequestParts } savingsAmount { value } createdAt}\",\"variables\":{},\"extensions\":{}}"
		headers = {
		    'content-type': "application/json",
		    'content-length': "2920",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': USERAGENT,
		    'vendoridentifier': VENDORIDENTIFIER,
		    'authorization': "Bearer "+TOKEN,
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		data = json.loads(response.text)

		return data['data']['me']['referralUrl']



