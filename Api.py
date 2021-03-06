import requests, json, time, datetime, base64
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
		'''
		with open(img, "rb") as f:
			im_bytes = f.read()        
			im_b64 = base64.b64encode(im_bytes).decode("utf8")

			url = "https://api.kard.eu/graphql"

			payload = '{"query":"mutation androidUpdateAvatar($file: File!) { updateAvatar(input: { avatar: $file } ) { errors { message path } }}","variables":{"avatar": "ee"},"extensions":{}}'
			headers = {
			    'content-type': "multipart/form-data; boundary=88ca1728-e2d3-4766-9346-1d0a9b31ab56",
			    'content-length': "70385",
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

		'''
		url = "https://api.kard.eu/graphql"

		payload = "--edbc727e-815d-4ab4-a3a6-2275aa698810\r\nContent-Disposition: form-data; name=\"operations\"\r\nContent-Length: 156\r\n\r\n{\"query\":\"mutation androidUpdateAvatar($file: File!) { updateAvatar(input: { avatar: $file } ) { errors { message path } }}\",\"variables\":{},\"extensions\":{}}\r\n--edbc727e-815d-4ab4-a3a6-2275aa698810\r\nContent-Disposition: form-data; name=\"map\"\r\nContent-Length: 27\r\n\r\n{ \"0\": [\"variables.file\"] }\r\n--edbc727e-815d-4ab4-a3a6-2275aa698810\r\nContent-Disposition: form-data; name=\"0\"; filename=\"cropped2039795875.jpg\"\r\nContent-Type: image/jpg\r\nContent-Length: 50655\r\n\r\n����\u0000\u0010JFIF\u0000\u0001\u0001\u0000\u0000\u0001\u0000\u0001\u0000\u0000��\u0000C\u0000\u0003\u0002\u0002\u0003\u0002\u0002\u0003\u0003\u0003\u0003\u0004\u0003\u0003\u0004\u0005\b\u0005\u0005\u0004\u0004\u0005\n\u0007\u0007\u0006\b\f\n\f\f\u000b\n\u000b\u000b\r\u000e\u0012\u0010\r\u000e\u0011\u000e\u000b\u000b\u0010\u0016\u0010\u0011\u0013\u0014\u0015\u0015\u0015\f\u000f\u0017\u0018\u0016\u0014\u0018\u0012\u0014\u0015\u0014��\u0000C\u0001\u0003\u0004\u0004\u0005\u0004\u0005\t\u0005\u0005\t\u0014\r\u000b\r\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014\u0014��\u0000\u0011\b\u0004\u0000\u0004\u0000\u0003\u0001\"\u0000\u0002\u0011\u0001\u0003\u0011\u0001��\u0000\u001f\u0000\u0000\u0001\u0005\u0001\u0001\u0001\u0001\u0001\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\b\t\n\u000b��\u0000�\u0010\u0000\u0002\u0001\u0003\u0003\u0002\u0004\u0003\u0005\u0005\u0004\u0004\u0000\u0000\u0001}\u0001\u0002\u0003\u0000\u0004\u0011\u0005\u0012!1A\u0006\u0013Qa\u0007\"q\u00142���\b#B��\u0015R��$3br�\t\n\u0016\u0017\u0018\u0019\u001a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz���������������������������������������������������������������������������\u0000\u001f\u0001\u0000\u0003\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0000\u0000\u0000\u0000\u0000\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\b\t\n\u000b��\u0000�\u0011\u0000\u0002\u0001\u0002\u0004\u0004\u0003\u0004\u0007\u0005\u0004\u0004\u0000\u0001\u0002w\u0000\u0001\u0002\u0003\u0011\u0004\u0005!1\u0006\u0012AQ\u0007aq\u0013\"2�\b\u0014B����\t#3R�\u0015br�\n\u0016$4�%�\u0017\u0018\u0019\u001a&'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz��������������������������������������������������������������������������\u0000\f\u0003\u0001\u0000\u0002\u0011\u0003\u0011\u0000?\u0000����(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000����1�?�F���i~\u000f�$EE�}�?gVV�U��\u001b��sW�P�ǟ\u0011QAwm%����40���5\u0005ݴ��p\u0014W��\u0007���y�(\u0016}r���\u0011�1\u0011L|��\u0006�VT;@#-�Ƿ�\u001e��\u001f�'��iu,�/ץ��9Ȋ�O_)&�\u001dX��9�\u000fj�,_\u0019�XNd�\nN=\"���Z?��<W\u0019dxNd�\nN=\"���Z?��z�����t�\b�y��c�K3\u001f`:����c\u001f�\u001e\u001b֦�\u001aD��O\u0002Ė���X�`ę\u0007}��\u001e�\u001fS^�\u000f�<9o�Z�ái�^Z�h'��\u0011�$`�@����x���톡)��j:�??���b�K��v�P��ݵ\u001d\u001f��s��ÿ\b�m⶝t�\u000bj��\u0000�A\u001d�|��:�c]v��'|T�d�\u001f����m��e�t'9cӌgԁ޿Rh����v>W�4!\u001e׻�Q�\u0015�L���Ƅ#���?=�O�'���\u001b\u0005��R����H6�J�0\u0000�r�W��tz\u001f�\u0013�V�P1j�)���[esqgne�9��EV*v�\bK\u001cr�\u0000������j���T�-H�������\u0000\u001b�\u0015^?�j^�#\u001b������n|����'�����u�\u0011jڤ����\u0016;P���\u0011&O�E_��\u0000�}�<�4\u0016���\u000b�\u0010�=�N\n\u0006\u0005�\u001eX�# \u001e��\u0007\u0018��(�\u001e\\]��\\�\u0015+������K�s�K����_rV>��\u0000a���C����u��v�^�:c\u001f�\t��[��ǟ\u0007�\u0000�N��\u0000\u0003����{%\u0015�S�s����.��r_�8g�9�IsK\u0017S�9/ɞam�1|,��8S�:iH�*�\u0015��\t<�\u0012O�<���1,�_���\u0019|\u0011��\u0019Xf\u001c��B2\t��� �\u0005���>�Er��1n�\u0011?�\u000e_�r<�1n�\u0011?�\n_�p��\u0000\u0001�\u001cj0\bf�/��\u0003\u0006�\u001atQ6G�H���85�߳?��FC��/\u0005J�FA�\f:��\u0018����\u0002=2�����+F���\u0000\u0014�̘���+F����/�<o�\u0018���\u0000�\t��\u0000�}��\u0000\u001d���أ�4�K\u001ahw\u00103��\t\"��r\u0002�l\u0019$m\u0007��NG$�+�(���\u0006o\u001dV.��\u0007/�:�����b��r�\u00003���w��_���\u000f�\u0006E�\u0000�j���\u0000\u0004��EՁ�I�5�>�p\"{���\u0000�6\u0005O�u}KEwG�s�IIb����z\u001d����\u0012RX�i��\u0019�.��\u0000\u0004纊�N��8nn���fa�f\u000eHdg9�8ǯ5���\u0000�=<q\u0005��\u000e��\\Ƚ\"G�Ks�P\n�\u0000��j\\}�SVuT�c\u001f�#֥ǹ�5gUK�1�\u0012?.|]�&�M�z�%Ǉ��\u0005�8�[\t\u0016`�ܢ`\u000ey }7.z�'�|\u0016���#�5?\tj։��^վ��\\�=YG�_�TW�P�70�J�\bK���V{�|K��%Z�%��_�?\u0016�\u001a'du(�p��\u0004\u001fCI_�rx'óH�I�i�#���g\u0019$�����>1���\u0018���]�x}ln\u000b��>�)��f ��pzq��_M��;\u00059[\u0011��WtԿ\r\u000f��x�������+�j_����\u0015����\u0000���\u001a�����ڥ��w�V\u001b[�\u0012C�w���n铁�^]�\u000f�'��4[\u001f�h����\u0007Tw��i�s�\n�g!�r9 \u000e9班�q�E�K�����k�{~'�a8�#ť��F�I5���\u0013��+ѼW�:|G�F�q�k^\u0015���m���$�@��d�b@��\u0005y�}�\u001f\u0017��ǟ\rR3[^-5�\u001f_��a�q���S[^-5�\u0005\u0014Q]GPQE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000Q]'�~\u001a������\u0017��\rLN�#�\u001bv��\u0001�<�����}!�O�'ǈ5\u0016Y|W�[i\u0010�`��#ϔ�ߕ�\u001c(��\b�\u001e��f9�Y�/���/���Wg����nV���(�ۿ�]�%���|\u0007���]��}\u001bK����l[�B��Rۏ\u0001@��8\u0003�~�x\u0007�/�\u0007�tH���?��U�J��1\u0004\u0015}˵z\u0000@PA�<׺[ivVB�[�A\u0000���\b�%_)\u000e2���;W���=+�\\�ļ5&ဢ��W����V��\u001d�ͳ\u001f\u0012�ԛ�\u0006���^Z/'m[W�v>\u0000��\u0001��d�&��i�\u001e��VX̆�uO�*��~��J�_\u0007��\u001f\u000e�!\u0014��ڟ�g�vJ��}�\u0002�\u001f:�[]zp\f�9=x��tW�X�6�1�{nE�\u001e���~'���5���{nE�\u001e���~'\u0013���ǃ�\u0018�}�@��m��⛷�Z呤.#iq��r\u0014n$�W$����\u0000`p\u0005\u0014W���V��uk��Ov�����\u0015�5\u001dZ�r�ݷv\u0014QEs��E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0004w6��[�oq\u0012O\u0004�RH�P��x ��\u001a�<e��þ:��χ�]2�K\t�h��\u0004e��FE�-�B��;N8���ڕj�d�JM4���ڕj�d�NM4������7�+�={í\u0007��O�5�p��5��\u0011�;q�냐:��𯈟�G�|3\u0011����m��m��!T6�9c��\t+�\u00122w��\u0000\u0003_�\u0014W�e�m��-\u001fm�\"�����~��}�\u0003�s�\u0005���������~��~Dx��/�~\u001dk�i\u001a��skx����_66F\u001c2��H��\u000f\u0004\u0011ڹ\u001a��tY\u0015��ea�\b�\"���_���\u001f�Zu��H�t�Y�+\u0005���;\u001c)ٕ^\n��F2qֿE˼M�7\u0018f\u00149v�����+�|��\u001e]�]9��\u001fC�k�.�����l��������\u0013�Z���O\b��j��Y��G����e`\b#�\u0018�����<e����\u0003��쵍\u000e�&�P��\u0014fH�\t!\\��\u0000�N3��C.�\u001c�5_���}�}�vg��w\u0010e���\u0000e�������9\n(����\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000���<\u001d��Ğ?�{_\u000e��z��2��<���t\u001f�eR�:0u*�F+vݗ�eR�:0u*�F+vݗ�s�-����\u0011��C%��0T�%,�O\u0000\u0000+독\u001f�6�w��s�ˤ�����g�͙�BX\u0005-�\u0014\u0000\u0003\u0013�\\z�֟\u000f�\r�;ᕜ\u0010�B���%��^0�,J�bd?7 r\u0006\u0007^+�<��\u001c�\u0000�</�����/�O���6���\u0000�</����~�\u0000�L�o���/��\u0019�oy�Im�\u001d>C�ޫIw�nC\bF1�\u0001\u000e�G'\u001e�K�6��~\u001e�\u0019��S�_\u0016j\u001eZ�6�\u0014ۇ�C��\f`��\u001c�\\\f\u001e��\u0003E~5���s�^.����\r?\u001f������eƙ�ex���}!���~?\"���k��Ekgo\u0015��J\u0015\"�\u0002��0\u0000\u0002�QE|3m����m݅\u0014QHAE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001Q�o\u0014��Ď\u001ca�(;���IE4��Ӷǆx��2�i����M:\u000f�� w�G�D\u001b\u0000�yl\u001a1�䐠�:�s�7į�7�>\u000e��5\u001d\u0003Q��e�\u0011�5�\u0010<7�rA\t\u0017�\u0018\u0001��������e\u0015��g\u0019g9cQ�g8/�/{N�z��>�,�\u001c�-j1��\u0005�e����_&~3k\u001a.���Bk\rN��O����ou\u0011�D>�O\"���G��\u0007��\u0019F���Z~�Z&�̺�W�P�!\\����#\u001dk�O���O{[��f�N��\u001bq\u0013\t��Rd,��U�\f\u00028�\u001cc޿a�|E��~�:.���\u001f�j�����U�&_�|�غR��\rW��>\"��\u001a�0�O��٭�A�]��6\nfxɉ��a�\u000788湊�N�ju��Q��_T���iV�^\n�))E�N�(����(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(����\u000b�K�KZM3Úl���KH~X�\u0000d�s����V5�R��ukIF+vݒ1�Z�\u001e��ZJ1[��G+]����/���}��Z4���\u0005����h:}�\u000f�\u000e9�2�g\u0000��\u0006a\u001d\u0007C����w#k:� w��}�з͕f^d�W�\u0003 ��k�m3K�Ѭa��� ���m���5�4\u001e��\u0000\u0003�_�g~#a��Tr�{I/����o/�vl��:�\u0017\r�r��G�I}��~Ky~\u000b�g�?\u000b�`?\u000e�֫s�{�5��Nm,ݡ�����\u0018w �\u00198\u00047�\u0004WӞ\u001d�Ƒ�-6=?E�m��(�X-b\b��z\u000f��:+�\f�;�3y�c*�.�Ez%�?\u0012̳��6�62����^�h\u0014QExg�\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000Cweo\u0017�u\u0004W1g;%@˟\\\u001a�����%�O\u0017\u0011u�[��]A��Y�F�\tCs�!a�\u0007��\u0000$`���(�_-���MOk����\u0000\u0007ꞏ��_.ͱ�MOk����\u0000\u0007ꞏ���?��\u0004|g��xS��;��;�Au\u0014�,3m=C)8��\u0006��j������+�y`�$�\tT��ȡ�Ԍ\u0010A��;W͟\u0014�a_\u0006x��I�)�����)\u001a�Km+a�\f�K.I^T�\u0005�k���Ě\u0015�K4��/掱���˛�~ٓ��B��f����GX������?<h���g�?\u0017�$��\u001f\u0012iMl�&������q���>���W�X|E\u001c]5[\u000f5(��wG�\u0018|E\u001cU5Z�Ԣ�i�\u0005\u0014Q]\u0007@QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0000d�s@\u0005hh^\u001cռOx֚6�y�]�\u0019\f\u00166�3�\u0004\u0002�T\u0013��ϸ�r�\u0011�\u001e��⠇T�\f�\u001d��d��#\u0006yʜ\u0015H�\u0004\u0003��x���_x|/�A�o�Z*��\u001c�c�����EV���$\u0019d\u0000\u0016��\u000e�<\u0001_��\u0007\u001c�r��a�\u0000{UtOE���-{���?��\u000eR�\f?�j����_%�{\u001f,�\u001d���\u001d�5O\u001f�,J\n���dw\u0013�N�d���!}8c_b�s��G�t���\u0017N��,�\u0018Xm�\b��_Ƶ(����?�3��c*]-����~����}ͳ��:�62��H�\"�_���\n(��t�ࢊ(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003#�~\u0014��k��h�ͪ�i� \tbn�\u001c��ҾO���\u0000C�\\^_�#T�O,�å��1�\n\u000f�9#���\u0018���}�E}\u0006U�f9,��UZOu�_�zt�3�ʳ��&��u\u001aOu�_�zt�3��Ş\u0006�\u000f�����t[�\u001e}��.�dY\n\u001c1F<8\u0007\u001c�#��5�_�_\u0011~\u000e�C��\u0011��}\u001d5'�'�\t���\bb�J\u0015#\u0007(��c� �Y���\u001e�<\u000fk�k�\u0016���Э��Yɓ|���$\u0005\n�q�s�q���\f��0\u0019��\u001c_�\u0000\u000bw���\u0000��O߲.;��\\�q����-�K;�v�>`��,O\u0004�\u001c��Ȅ�#�\u0015#�#�6�P��;p��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000���?�7�_�|M��Z�,��o�r�M\u0001UV��R܄Rv6�C�?yHV\u0004��fY�\u000f)��\u0018ʊ1�[����\u001e^c��2�\u000f\u0011���\u001fž�nߡ��\u000f�\u001b���v�4�\r��j\u0017@\u0006��\u0002D���c�\u001f��k�?���o��\u0001hn�J���[�9bc\"�o\u001a8�B�������\u001cc��?��\u000b�7��E��t\r6+T����APg�g,]��$�{z\u0000\u0000����x���y�t0Mҥ��K��^K�s�߈��\u0017�7C\u0004�:_�4�_E��w\n(��.?0\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��<C�����ό���2h> �>/m�\u001bg�N%Q��c��y<�_\u0001�X�/���ɲ��Y-�v[[����Gu=�1���Z�\u001b�\u001e\r�<i�Ic�i�ڝ���En#\fUXa���N\u0007#\u0007��_���\u001bcrnZ\u0015�\u0000yEt����\u0000G�k\u001f�p�\u001ac2nZ\u0015�\u0000yEt����\u0000G����E}S���'ռ+%���x$�4cr\u0002h�����\"��\u0002F\\\u0007.1�\u0005\bIl�_�%�����\u001a7^��\u0004~\u0015�!���<₯��2꺯&�?�\u001fѹ^o��(*�9�.���k����(����\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n��ǆ5?\u0018��z6�g%��v�8��d��}\u0000�Oj�>\r�\n�?ƍz\u000b=\"�H4�&۽^X����`�OF|\u0011�\u0007'=�H�\u0019�'�+@�'��,4�[��g�Y�)�\u0002yT�yjǶ�!x�'q��E|\u000f\u0012�~\u0013\"��\u000bN��=���zn����q'\u0017a2(:P��t�o9>���MO\u001e�\u000f�\u0010�\u001e\u0013X5\u001c\b��_\u0019]8|��0l���<\u000e�}k��P�\u0015@\u0000\f\u0000;R�_̹�o��+�|d��E�y%����ә���޷��O��]\u0017�]?��\u0014Q^9��\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005x\u0017�\u0013�(i\u001f\u0018֛̚*�\u001e'H��UG�v@�D�����{�\u0015�e��++�,N\u0012|�_���TzY~c���\u000b\u0013��,����T~?|@�y��2�%ƅ�\u001b3g}\u0016\u0018`�$S�ѿ�O�su���;�g��,�b�D��\u0004�J?ws\u0018\u0002kw\u0019���\u000e\b��9 �\t\u0015�����m�G��V�il������m�[�TH���3mP�cnF\u0000$�����[�8�\r��a�\u0016�_�����S�O�x�\r�EP�Z\u0015�_I���3�袊� �\u0018(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000+�o���J��*^A�x�\u000b�#�{\u0004�66Kx\u000e@\u0011�\u001c\u000e>�\u001f�k���?dmKĞ!�^�Β��\u001f�Q,Z}����B���]�1a�FA��#����� �#�\u00168�\u0005TA��t\u0000v\u0015��\u0017q�����rNmk5���|��z���\u0016������$���kU\u001f%����l�\u0007�CI�'�l�=\u000e�,t�D�\u001cH:��\u001e�O$���E\u0015��R���Ԩ�ޭ��?�jT�Y��woV���\u0014QY��\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005Tմ�=sM�ӵ\u000bh�,nc1M\u0004˹\u001dOPE[��d�Ԣ��Q��R��G���o�a{�����\u001d�֫�\u0015f��ϙ=�\u0001bÏ�0>��5��~���ߴ��`�&��|Y�q\u001d����\\誘K�3��\u001e��d��N:d���\nq�3X,�^Q����\u0000�}��ݸW�������\u0019��_�����N�}ż���\u0004��3D�\u001e9\u0014�#\u0003�\b=\b=����w�\u001f�'}PQE\u0014�\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QW�\u001d\u0003Q�F�i��\u0016Sj\u001a�ۈභ]���?2O@\u0001'�M��&쐛QW{\u0015-�����\b#y���$h2���\u0000;����j��,|1\u0006���\u001b�nu�a=���0�t�1�8<�8\u0007����f��7K�Mo\u000e��,:��]c�3 h�\u001coȈ�$�\u0000��A\u0018����ߋx�X�l\u000eU&��)�\u001c��e�������8�X�l\u000eW&��)�\u001c��e���ܢ�+��񠢊(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003���k�K�~&���t\u0016���4V�$�E\u0016��\u0019F@ tr\u000623�3�_�\u001a΋��R�M��&���s\u001c���W��b\r~�׋~�߳F����\u001b�\r�����mLC�IQc�$L�����\u000b�J�{���yw.\u00071�5\u001d���˻_�����\t����\\\u0016b�K���˻_�����En���\u001a���\u0012^h:��Y�\u0016��S�]{:��z��\u0000׬*���R\u0015��Sw��5�G�]:��\u0005R��^���\n(��4\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��&��MZ�K��%��.�\u0011Co\n坏a�=���Q�\\���2��r��B�z\u001d�\u0000�5k]3K�����A\u00140B����\u0000W�\u000f���2�|\u0017�WT��;�\u0017�ǉ�\u0007+j��YF�&��\u0014~̟�-��}!u=Mb��}���\u0003)j��YE�[�ҽڿ�xǌ���X\f\u0004�En�\u0000��\u0000���\u000f�\u000e0�\u0019fR�\u0003\u0001+Q[���\u0000�0��+�3�P��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003��?|\u0000Ѿ8�h��\u0004��m��\rL/1��\u001f��{��G��_��\u0011��<�%慮ٽ��j�Y\u001b�\u000ȩ���\"�b+��?�\u0001Ѿ8�h��\u0005��mT�\rMW-\u0019���\u0000�����{����_<�k\u0007�w���\u000f����k[��w\b�t�y�&-ރ����.�浺��V���\u0011��=�%慮ٵ��j�e<��gS�J{\u001a¯��u!Z\n�7x�S[4Lө\n�U)����٠��+C@��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0002Kkin��\b#y���$q�Y��\u0000\u0003����\u0000�S�^��m�����%�\u0000���݃Z�\u0005\u0016��s\u001b|�\u0019�\\�\u001bO�A\u0015��\u001d��־\u0014Ѭ|q�[F\u0010�/�ggs\u001e߱&H\u000eT�\u0000\u001b\u000eG�#�O���ߍ����<�\u0001/q]N_�ѥ��������8���,�\u0001/q]N_�ѥ����ܢ�+�s񐢊(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003ſi�����_��k$�\u001f\u0015X�~�q+�F\u0019\u0005� \u001c|�\u00001\u0007\u001f�~hkz\u001d�\u0000�5k�/T�����C\u0014��.�F\u001dA\u0015�1_>��\u001f����o\f\\k�-�|ea\u00180�8S{\u0018<���B��둎����+��Y8���z2~��F�\u0000��׶��ָ/�^[8���z2z?�o�\u0000m}{o��ܢ�qo-��A<o\f�1G�E*����\u000fB\u000fjeJ'}Q� ��AE\u0014S\u0018QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000W�\u001f������&��\u0003��\u0003c\u001b���\t\u0017�s\r��Tt����U�#5��\u0000����u�wZ�]��\u0000��+��<��&�E���\u001c�t�Oc�_�qD�D�Ƌ\u001ch\u0002� �P:\u0000;\n�[�����y^\u0006^����+�W���z���\u001c�_�b��\f�����*�}{/]\u001dE\u0014W����\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000|��i��m�\u001bT񟄴9nu�buT�*\u0004��1�J\u001eY�\u0000|�$\u001eA�\u001f\t��-|\u001f�g����P����maM\u0012r�P��v��Bq�c��$g\u0018�=9��8\u0013�>\f�\u001c��&�\u0000�W����~���W��\u0018��\t7�\u0000������|�E\u0014W�\u0007��E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001^��+�ޫ���6�E�\u0012�2'I5;��m����A\u001b�\u0004*�>����c�\u001a��u�M\u001fF���Q�q\u001cP�2I�>�w'�~��\u000b�=��\u0015�,\u001a\u001d�I5ĭ��ۙO3NT\u0006 g\n\u0000P\u0000\u001d�s�~\u0003���9\u000e\u0013���i�+��'�ӻ�g��w\u0012G\"��Rw�?�v]d�:w~��|\u001f��#��\u001e���;4�ӭSlq ���{��I�[4Q_�U*N��J����ݳ�Z�I՛���շ�aE\u0014VfaE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001U5m&�\\�nt�B�+�\u001b��SA2�GS�\u0011V��\u00198�(�4Td�Ԣ�����O�\u0001��/�I�����#~����m�\u000eܴ.q�\u0003�\u0019��\u001c�\u001b\u001e1_��\u0000\u0012~\u001e�_\u0014|\u001b��kYY\r���^\u0016������}C\u0000px8��*�&�9վ\u0017x��\u0000@����H$>L��\u0013œ�E�#\u0004`�N:W�\u001f\u0005q:ΰ�UĿ��_�\u0012�o_����O�_\u0013,�\r�\\K��5�\u0000�/���o���+E\u0014W���AE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001J���T\u0016bp\u0000\u0019$�W�����~(����W\u0006?\u000eh���Sùo��a\u0010,\n�\\\u0002�N\u0019F>l�/3�heXI�1\u000eъ��D��<��1��a'��;F+�}\u0012�l�����u��w����\u0012Y�<A}\u0018[X\\���\u0011�a�3q�P8��袿��\\�\u0011����Ŀz]:%�/%�\u0000\u0004�>�s<Fo��3\u0012��}�tK��\n(����\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n����R|Y�3�:t*|I�#Kn�q2�2�\u0010\u00039'\u0019\u001cu�׼Q^�]���b��ûJ.�\u0000染ٞ�_���b��ûJ.�\u0000染ٟ�l��U�VS�\b�\u0006������\u0000��p�\u0010�?i\u001cVw\u000e��ֶжVRX����V�[���O�\\������sz\u0019�\n\u0018�\u001a_u�5���Z���6mC:�C\u0019CK�_��P��+�=���(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003��\u000f���>)����\nͨ]nټ�E\u0000\u0012K6\u000e\u0007\u001d}H����^\u0004��i�=\u0017�6#0X@#/��!�;�vb��׏���\u0000\u0002��/\u0005\r{S�\u000f\u0010�q��\u0016P�\u0015���Q��H9<�����=/��\u0011�\u0000kb������\u0000�)lߢ�|�S���8��W\u0015�<;��7�\u0000�Kf�\u0016����\u0014Q_���\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0014��\u0016��Z5����.,/a{y�$���*ÏPM~S|o�O�� ����y\u0007�i#��.\u001fx{r�\u0013-��\u0000\f�ٯ�j�_�W��_\u001a>\u001f�g\u0002\u000f��\u001c�i�d��ɎQ�\u000f\f8��9\u001dk�.\f�/�Lo���\u0000sR�^O������\u0007�x��\u0013\u001b��?�Բ���/���?-(�.������e�4Ncu�8`pFG�����4���R�j�(��c\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n���+�,�\u0016|_��k\rǆ���7q�; �c�\u0011p\u000ep\u0006H��\u0002FEx��4+�\u0013��Kѭ\u001a5��n����$ y\u001c\"� \u001c\f��\r~�|\u001f�a��\"�\u001e���9\u0010�(\u001e��A\u001fi�*\u0004��I�H\u0018\u0019�\u0000;W��o�/'��\n\u000e�j輗W��y���㍸���/aAڭ]\u0017���z/7~�a\u0004\u0011�C\u001c0ƱC\u001a�H�B��\u0018\u0000\u0001�\n}\u0014W������E\u0014P ��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003�/�W�>\u000fդ���cok��̱\\�lNb��;��\n�A\u001c\u001cg\u001d7\u0001_+��g�|#����:���[-ޙ}\u001f�4D��A\u0004\u0011� �A�@�ɿ�\u000f5_��3Լ;�C$sZ�DR�m\u0017\u0010䄕y#k\u0001��\u0007 �\rMp\u000f\u0010��\b�\u0018�~���ޏ�����K�\u001f\u0010<�\n�8�~���q�Z���^�(�Տ�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�+��]��Q���m7Úb\u0006����X(�!˾O���5�S�ҕj�ъm��\u0018֭O\u000fNU��F*��H���\u000b�(�$�\u0000\u00115X#(���R�\u0005��$�\u0004q��\b ��c_i�/��/\u0007��)�h6��[��-�>���������7��j��aS\u0017=��Wh�����\u001d���L�0�����>Q[��l(����炊(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�R��~\u0014ǯ�F��60gS�$\u0016ӈ���\u0003�3�����p\u0001oZ��������ky�K\f�ctn��`��\u001a�rlΦO�����+�w]W�\u001e�O���1�����z������~����\u001f�\u0015������[�\u0006�r�u�H\u0018\u001d�\u00168�t �1�^e_٘LU,n\u001e\u0018�\u000e���?����X�\u0010��w���QE\u0015�u�\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005}��\u0004�#���-w��F��\u0000j����\u0012\\BT�\u0000\u0003s�I�\u000eI\u0019\u0003�\b�\u0004��_\u0007>\u001b��W���xj�zGu0k��gɁy��`\u0010���\u000b\u0015\u001d���K�-tm6�O��m��!H �:$j�UG�\u0000\n�o�l���h�t_�SYyEt�\u0000����s��\u00113��a��Q~�Me�\u0015����}�4QE9���E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0007�~��\u0006��#�4��l�\u0011�E��na�W��[�L�g#�e�s��\f���z����_ڋ�!�I�[Q���Ǣj\u0004�i�\u0003�cbwD\u000f�\r��I۴������ۜg�֖��=>��W�?z��:s�����އ��_��g�QE\u0015����QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QEt�\u000e<\u000f{�\u001bƺO�l\u0015��Ӭl�g�L��~�'�ʭXP�*�\u001d�\u0014�}�2�V\u0014)ʭGh�6�d���`?��h�\f���ʤ�������L6��\u0018r���\t8$\u0010�Њ���hzE����i�����B�F��E\u0001F8\u0003�Wk��:������g����Z%�G��s�O6���O�=\u0017e�_$\u0014QEx��\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0015�_����<y���U�Q5O\u000f���V\u0018-\u001e?{\u001ev���\u0001���O\u0015���#Ycdu\u000e�\n���#Њ���uL�\u0019K\u0019Kx4�{������uL�\u0019O\u0019Kx4�{����\\��\u0013��Û߆�\u0013u�:�������V�ci�ؕ��8��Ҽ0��x�\u0010�Rw��k�g�q\u0014�t!���\u0019$��(���:��(�\u0002�(�\u0002�(�\u0002���\u0000�~|-1�������Y7i֑�&X� ���\b `g<���4]\u001e��\u001a���a\u000b\\^�L��ă%݈\n\u0007�E~�|8�t\u001e\u0000�&���\u0015\u0015t�D��E���̌7s����_����<\u001e]\u001c\u00157�Vz�\u0000�o��/����,����੿z���+��}�GE\u0014W�9��\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000|��x�6��\r`�E���P�%\u0002I\u0014�ų�6��@m�\u0003�Ǌ����\u001f\u0014x~/\u0015xwQѮ.'�������Ԩ�#\f0\u0005���H�޿\"�u�\u000b�\u0002x�Sе\be���]�fB��F�m���J�}k�7�l����e�~�7u�\u0017�O�?��7�=�\u000e�_7�Sw_���\u00003\n�(����B�(�\u0002�(�\u0002�(�\u000f��\u0000a�\u0001Zx��'���I!�mM�Q3�Z}ꑝ��!w\u0016�\u0006\u0003*d��G�Ŀcχ_���\nim+��k-��8=#�\u0015B(\u0004\u00020��\u0007?6�q����G�,��W7�(?r\u001e��^���%��i���Ԕ_�\u000fq|�w�w\n(��\u001c����(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000����>\r���^\u0016�D,�-���\u0017\u0011�E$������$H�� \u0005@q�����?i/���'�\u0016��ǧ\u001dGQT\u0013؄h���NU�?\n1����`:��p�d��ގ\"o�o��KK��#��[2Y^oG\u0011'����i-/���~T�J��;#�GS�V\u0018 �\u001aJ��?�\u0002�(�\u0002�(�\u0002��\u0000�~\u0003����\u0013C��\u00104�ur�h�H�\b9��\u0001���3�Er\u0015���\u0013����\rw�r\t\u0016\r>�Y��뵤��\f�{�PA\u0018\u001fZ�� �?���������z/ş?��\u001f�ye|Zz�i��_�>췁mm��3�5\b��\u0003\u0002����0z�\u001a�}B�(�AE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0007���M�a�?��\"��\u0001my'��\u0003~��\\��\u001dwn��\u0015���7�\u0014+��y��\u0000\u000f��\u0014v6R���ޡ\u0015\u001f�8���\u0018��\u000e���ap�c���Ь���+���������)��\u0000i��+7y%��c����aE\u0014W�\u001fX\u0014QE\u0000\u0015���(x\u0016/\u0003�\u0013�\u0010ٛK�B/�����g9RH��n\u0007l�����\u0000\nj>5񖓣iV\u000f�^\\�(\u0016�\u0007̠���\u0001B�I<\u0000\u000ek�\u0002��\u001b\u000bHmm�X-�E�8�aQ@�\u0000v\u0000W�>&��(P���M��-\u0015�f�����K��P������ע�]vm����(����\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003�����~&|/�t �,�@e�D��Ҡ,��\u000e�\u0001��ֿ&f����)\u0014���VS؃�+���(h�\r��_�>.��kO����$�9�%s�G�a�;Xv ����\u001c�\\،�[i5�?����<|���%��_��\u000f8��+���p��(\u0003�?�'�����/T�,��\u001a\u001d��ep?}6QA^�`��@��*���\u000e�e���Qu����ׯ%��T��\u001cNФd��\u0000��:�#��\u001b_�\u001ck���y]��=��\u0000n��\u0000�k�ɜi���w]��=��\u0000n��\u0000�k�\u0014Q_\f|8QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000W�?�QO\u000eH��K^�La\u0012��S�a��I�\u0014%s�\u0018���;��}�^=�[�<x��\u001f�#H�{�>%��y�<�%���p~c\u0017���v8�k�8S\u001c���\u000fY����%���{�W¸���p���\\��^��W��wE\u0014W�!��\u0014Q^��:xb���\u0000\u001b|\u001f��\u0012-��L�h`�R��H<\u0010J\u0000}��\\V\"8L=LD��r~�7�\u001c��Dp�z���\u0004��\u0012o�?O>\u001bxF��~\u0002�<=g�ç��\u0007�\u001cB!+\u0005��*:36X��bI5�P\u0000\u0003\u0003�(����gZ���w��o��\u0011ի*�%Vn�M���\n(��2\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n��\u0005��4\u001dF�[[^��y\"\u0016���%ܤm���Npx<v5�ETd�%%и��JK����]\n_\fx�Uѧ�%�N���I#��hܡ#<�����\u001f�?��ᯏZˣ�c����R4�#ܻ\b>���g�������1k\u001f���_n)����?���Z�����ۊ6��B����|?u�[R�`�$Z}�I��\u001c2��\u0000\u001d�U���\u0015�\u0003\u0002\u0006A������'ǃƛ��Z�\f�D%��<��V%�q�\u0015#��X�5�\u001cm�XL���;E|޿�Ϙ�\\Z�du�Y�+���.}YE\u0014W�I��\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000|Q�\u0000\u0005\u0012����º�\\[\u001d=|�$�ca0����d�\\/\u001c\u0002=���5�3�ux^�_�8.�,���.��i2\u0001�<\u0015f\u0019���Z�����\u0000�}c#�\u0006���\u001b�����\u001cO�2:poX9G���¿Qd�\r���\u0005�~��{o<��g��\u0016��Gl���e1�\u000f9�S_����]�E\u0004(d�W\b�:�\u0013�?:���}��\u001e\u0013�-�#1O\r�\u0011�\u001buV\u0011�A�E|��ؗ\f\u001e\u001f\f�ԛ�\u0000�W�\u0013�|Lĸ`��u����\u0002����QE;��AE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0007\u0015��H��~\u0013x���܋yt�w}�3$�\u0002F�\n��\u0007c�k�<�\t\u0004`�ƿik���\u000e�u����\u0016W����7�,�?U;���~\u0017�o\u001cV\u0015�\u0000v[����]�\u001f�xc��q8gӖ_�z|��F���\u0016��?\u0018|\u001f��!���R�dEb����9�_�����\u001d�i�\u001f�65$\u000e��d�%�&\bLg���׏Z�=�\u0017���Y�\u001aZ�0�����k�<o\u0012�9f4ikh��Z��ݯ�(���x��(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000+�������\"\u001f\u001d<Mh.��\u0017\u0012���RK�*��I$�3���e~q~ݲ��\u0000\u001c�T���\"X�$����GnC`�00�wֿX�ִ��Κ�Pw�5o�w?V�޴��N��Pw�5o�w:\u000f�'�1��C�.Ȭ��\u0004�\u0011��Ό\u0012=8$~5��|]�\u0000\u0004䶴1��ᢄ�)��%*<�\u0019�\u000b\u0000z�$)#�@���k��ھ�?���E������u}�}Y*��\u0000�S�B�(��O�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�4�\u0000���\u0018��,�5\u0012�nԾ>b\u0000���NO�_e���PK+y~\u000e��O\u0004Ou\u000e�\u0014q��\u000b��R�\n�@;W u�=+��6��ϰ�����_��\\\u001dW���iwm}�����\u0000�|xJ���\u001aǉ\u0010H5+��,d%�C\u001a$N�c��n�������\u0000F_�\u0017��\u0001���$u\u001eT#?���+.-�*��)��ҷ�leŕ%S;�9;�V� ��+�O�\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\"����\u0016�g\u0011Ƽ�n����4��\u0000�'\u0007�\\w�\u00134��\u0000\nu׊F��\fC!�\u001c\u001a���\u0000��V�\u0000�����\u0000o���8c�\u0017\u0010��]���v����3�+�0���rr�ms���\u0013M\u000f��p~t�i��\u0000�N\u000fο!�$տ�'w�\u0000��h�\u0000��V�\u0000�����\u0000o����\u0000�_\u001f�\t�\u0000���a�\u0000\u0010��O�K�\u0000\u0004�z�\u0000��C�\u0000��\u001f�\u001f��h�\u0013����_�I5o�\t��\u0000���\u0000\u001a?�$տ�'w�\u0000��h�\u0000�_\u001f�\t�\u0000����C\u0015�\u0000A?�/�\u0013���\u0013M\u000f��p~t�i��\u0000�N\u000fο!�$տ�'w�\u0000��h�\u0000��V�\u0000�����\u0000o���!|�'�\u0000%�\u0000�\u001f�\fW�\u0004�\u0000���Oׯ�M4?�\t����\u0000\t���\u0000A8?:���\u0000��V�\u0000�����\u0000o���\u0012M[��w���Ə����\u0000�����\b�1_�\u0013�\u0000��\u0000�?^��4��\u0000�'\u0007�G�&�\u001f�\u0004����\u0017�\u0012M[��w���Ə�I5o�\t��\u0000���\u0000\u001a?�\u0017����_�!�\u0000\u0010��O�K�\u0000\u0004�z�\u0000��C�\u0000��\u001f�\u001f��h�\u0013����_�I5o�\t��\u0000���\u0000\u001a?�$տ�'w�\u0000��h�\u0000�_\u001f�\t�\u0000����C\u0015�\u0000A?�/�\u0013���\u0013M\u000f��p~u{N�l�P���.\u0002�퇥~;�\u0000�I��N���\u0000����\u001f�O�F�������k��\u001e<�-������\u0002,�\u0001<o��嶖��ǃ��*��\u0013��~n[ikn�}�GJ*\u001bËI���#_�%wc�t��R\u0013iQ�+_¬�\u0004\u0016�P�\u0019耐u(2?گ�\u001f\u001cx�W��:�.�x\u0014^J\u0000\u0013�>���/�I5o�\t��\u0000���\u0000\u001a�җ�J�\u0014�'t���\u0000\u0004�Ɨ���\u0014�'t���\u0000\u0004�z�\u0000��C�\u0000��\u001f�\u001f��h�\u0013����_�I5o�\t��\u0000���\u0000\u001a?�$տ�'w�\u0000��k_����\u0000�����\t��C\u0015�\u0000A?�/�\u0013���\u0013M\u000f��p~t�i��\u0000�N\u000fο!�$տ�'w�\u0000��h�\u0000��V�\u0000�����\u0000o���!|�'�\u0000%�\u0000�\u001f�\fW�\u0004�\u0000���Oׯ�M4?�\t����\u0000\t���\u0000A8?:���\u0000��V�\u0000�����\u0000o���\u0012M[��w���Ə����\u0000�����\b�1_�\u0013�\u0000��\u0000�?^��4��\u0000�'\u0007�G�&�\u001f�\u0004����\u0017�\u0012M[��w���Ə�I5o�\t��\u0000���\u0000\u001a?�\u0017����_�!�\u0000\u0010��O�K�\u0000\u0004�z�\u0000��C�\u0000��\u001f�\u001f��h�\u0013����_�I5o�\t��\u0000���\u0000\u001a?�$տ�'w�\u0000��h�\u0000�_\u001f�\t�\u0000����C\u0015�\u0000A?�/�\u0013��<c�H�WR��8\u00035�\u001c�*\u0007C�O ����o�jڷ��+?�\u001b�\u0012�F�y��p�z�gҬƟ�[ۆ-��\\�ɯϸ���ó�MU�sM�kX�\u000e'��p���U�sM�kX�E\u0014W�\u001f\u000eEss\u0015�-,�,Q�Vc�*��%\u001aO�\u0004 �\u0000��ſm\u001f\u0013ɡ�!���w����+��[\u0001�\u0011_�_���\u001f�\u0015��\u0000���5�w\r�T��\u001bźܚ����]��xs�����-��իZ�u��~�\u0000��I�\u0000��\u001f��i�\u0007P�r�d\u0011޿\"|\u0011}����zf�5K��Ϋ�����֏\u000f���\u0016�\u0013\u0012Y-�RORB�����cî�}�;��Z�<�'�����\u001fk��~����QE|)��E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001Y���M���-�Q������?շ��k�\u0007����K_���C��F��T��\u001c�z�\u000e\u0019��\u0000��\u0011:\u001eӓ�^����5��\u0018�������\\�'o\u0019h�pu(\u0001�\u0000z��\u0013M\u000f��p~u�\n|K�\u001e����\u0000���4�I��N���\u0000����_�\u000b��\u0000A?�/�\u0013����+���_�'���&�\u001f�\u0004����\u0000��C�\u0000��\u001f�~B�\u0000�I��N���\u0000����\u0000\t&��\u0000A;�����G�B��\u0000�O�K�\u0000\u0004?�\u0018��\t�\u0000����_��h�\u0013����\u0013M\u000f��p~u�\u000b�\u0000\t&��\u0000A;�����G�$���\u0004��\u0000���\u001f�\u000b��\u0000A?�/�\u0010�\u0000�b��'�\u0000%�\u0000�~��i��\u0000�N\u000fΏ�M4?�\t����/�$���\u0004��\u0000���\u001f��j��\u0013��\u0000���4�/��\u0004�\u0000���C�!��\u0000�����\t���\u0000\t���\u0000A8?:?�4��\u0000�'\u0007�_����j��\u0013��\u0000���4�I��N���\u0000����\u0000\u0010�?�\u0013�\u0000��\u0000�\u000f��+���_�'���&�\u001f�\u0004���֟��ڬ�+;��$\u000b��\u001eq�?��ǿ�I5o�\t��\u0000���\u0000\u001a�\u0007�\u0003���յm^����?��n\u0004�\u0016P|ȏ������\u000e\u0019>\u0002�5�/��۞\u001eu����51��_����O�袊����(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000+��m�\u000fE�~���̒�m��[�ƪ\u0006\u001d��'i����@�y�\u001c��\u0011����d\u0015K\u001f.��\f�.�'����*y�\u0012Qv��?\u0019$���*y�\u0012Qv��?\u0019$�\u0000\u0001?c��7/\u0007�s�\u0000�SW�W��ǟ�n^\u000e�\u0000r��\u0000J��d���m��\u0000���\u0000ҙ\u0019�������S\n(��3�\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��<�������f�\r�M4�\u0003\u0005E\u0019'�_�#�\u001e\"?�\u0007��\u0000�f�`��;��9QdF��\f�Y����\u001f�\u000e��\u0000�B�E��/�\u000fa�AR��w����7����\u0013��ss;�c�7�\u0015�\u0000��\u0000�\u000fw�\u0000~�\u001f���G�\u0000@{���k���\u0011}#������Q�\u0000\b���\u0000@�o��+��\u0000�'�����}w�D��\u0000�:�����W�#�\u0000�=���4¿�\u001f�\u0001��\u0000�ٯ�/�E���\u0007[߱G�\"�G�\u0003���أ�\"|�\u0000�\u0019}��\u0000\u00116�\u000e���7�\u0015�\u0000��\u0000�\u000fw�\u0000~�\u001f���G�\u0000@{���k���\u0011}#������Q�\u0000\b���\u0000@�o��(�\u0000��?�\u0006_x�M��\u0003�����\u0000��?�\u0003��\u0000߳G�+�\u0000\u0011�\u0000�\u001e�����r�\u0000�_H�\u0000�u���\u0015�\u0014>(|>�Wc$��vs]/K8UL����7���eEG\u000f�����ӆ�\u0013\u0013�������}\u0013?3��'� ���I�H�e��\u0000\n� �A�+ھ3�җ�\u0000\u0012$��N��Jҁ�<��#/�X�\u0015'''�~��U�W��1��$�'{z��e�q���Le5\t>��ޡE\u0015�x\u0003�?�>#�\u0011[h�t���\u0006�����k��zXjn�i(�uz\u001d�����խ%\u0018����K\u0010\u0000�<\u0000+��\u0000�\u001b�����Z����]\u00140���㞕��[�/��\u0012-�\u000f\u0011m�5U����A�\u0011_H��A�ۥ��I\u0004(0��\u0000W�\\a�x\\�\r<�\u0005\u001eh�^^��\u001f��\u0019as\f<��\u0014y��y?'}\t�\u001b��������55Cy�\u0000\u001es�\u0000�6�F�\u0015���^;�����:k���7��k\u000e�<w�\u0000#���\u0000_��f����\r�\bz/����\u0002\u001e��5��\tk\u001a�\u001e}��qq\u0016q�4ȫ?���G�\u0000@{���k����D��~\u0014+�g\f��\u001f��\u0013�W��\u0000�/��:�����{2�\u000ex\fe\\/��#��~A�x�,\u00062�\u0017�_���?#�_���������\u0000\n�\u0000��\u0007��\u0000�f�\\��\u0017�?�\u001dm�\u0000~�\u001f���\u001f�\u000e��\u0000�b������\u0000�e��o�D��\u0000�:�����W�#�\u0000�=���4¿�\u001f�\u0001��\u0000�ٯ�/�E���\u0007[߱G�\"�G�\u0003���أ�\"|�\u0000�\u0019}��\u0000\u00116�\u000e���7�\u0015�\u0000��\u0000�\u000fw�\u0000~�\u001f���G�\u0000@{���k���\u0011}#������Q�\u0000\b���\u0000@�o��(�\u0000��?�\u0006_x�M��\u0003�����\u0000��?�\u0003��\u0000߳G�+�\u0000\u0011�\u0000�\u001e�����r�\u0000�_H�\u0000�u���\u0014�/��:����?�'�����\u001f�\u0013g�\u0000@��?9�f\u001f�z���]=�t���\u000f���0\u0001\u0004W�h\u0018\u0000U\u001bM\u0013O��̷��\u00191�Ȁ\u001a�_��&> ��\u0011(r��X��������ה9RV�QE\u0015�gɟ\u001a�C5Ƃ��ZtoľcH\u0001�#\u0015�-}%�sx��O�w�v���HǦE|�_ל\u001b���G��ݫ��������7ղJ\u0011{����\u001e��/h�Y����+�\u0014�\r'�\u0006�S�B(Q�\u0003\u0002�>`�\u000f\r[�\u001d��\\��5�>���=~1�>'��Ѥ��R���\u0000S��\u0011q>�6�%�\"��v\u0014QE~T~X\u0014QE\u0000\u0014QE\u0000\u0014QE\u00006O�o��\u0000\u001a�����\u0000��j�_�k�6O�o��\u0000\u001a�����\u0000��j�_�k�\u000f\r?�cW�?������0��\u001f������9��J�ce5ү\u0004ƹ�gWۿ�N�e��P���;\t�\f��t��s����\tc\u00149�m=O������\u0019c\u0014y�m=O��_���������\u0000\n�\u0000��\u0007��\u0000�f�\\��\u0017�?�\u001dm�\u0000~�\u001f���\u001f�\u000e��\u0000�b�&�\u0000��?�\u0006_y�G�D��\u0000�:�����W�#�\u0000�=���4¿�\u001f�\u0001��\u0000�ٯ�/�E���\u0007[߱G�\"�G�\u0003���أ�\"|�\u0000�\u0019}��\u0000\u00116�\u000e���7�\u0015�\u0000��\u0000�\u000fw�\u0000~�\u001f���G�\u0000@{���k���\u0011}#������Q�\u0000\b���\u0000@�o��(�\u0000��?�\u0006_x�M��\u0003�����\u0000��?�\u0003��\u0000߳G�+�\u0000\u0011�\u0000�\u001e�����r�\u0000�_H�\u0000�u���\u0014�/��:����?�'�����\u001f�\u0013g�\u0000@��?#�\u0000�\u001f�\u0001��\u0000�ٯ�a�\b��g��ٿ�k{�q��\u0003�+��\u0017�?�\u001dm�\u0000~�_����?.\b�$��\f\n��!�i��'��\\���~��q\u0007\u001a�<�<\u001f��M�{�%��+�\u0003� ��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000�7�G���\u001d�\u0000�\u0006�\u0000�\u0000I��ʼ������\u0013�uX̄i��T/� ��\u001b��s��d�\u0001�},�<��\u0011�8�h�����hG����K�]�6\u001f\u0006<\u000b\u0014\u0010Gn�D���J\u0014\u0016xUٰ;�ŉ�I&���~\u000eB`�A�5(P�\u0000�?�6\b������k��3{��\u0012��<�\u0000��i���G\u0013Ϳ<�\u0000��\u0014QEy'�\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QP��Ac\u0003Ms4pD�������i6솓nȚ��U�m\u001b��\u0012]����\".���3}\u0005x\u0017Ə�GC�Y�Ӽ:\u0006����I\u001f�\u001fB+�\u001f\u001f�T�\u0017�}BK�cP�t,Y!-򧰯Ӳ\u000e\u0004��v����?=ߢ�\u00003�̇�����b�wO�w����O�_��q���3��`���x�\u000e=־M���G�w�{��K{t�e��j�:\u0018d��c�\u001aI\u0018�*\f��W�\u0016U�`2Z\\�H%��~���ʲL\u000eMK�\u000b\u0004���Ս�\u001d\u000bú��/V�L���v l�\u000b\u0011^��[�H�'ė��P���\u001c�3���~�E}����_�>\u0016YG\u001e�g\u001c�j�Z��oj�|���\u0019E�Q~үe��g�g�m��oJ���{-��>`�+�\u000e��4\u001a��$�a8�-�9'ف��|-��\u001f��z�h�0�@\u0000\u0004D�ݎ��@�\u0015���q\u0006?;�͊���+D�G��o�����ة��\"�K�\u0014QE|���P�ǜ�\u0000�Ϳ���\u001b��������5Q�\u0015\u001d������\u001d5�����\u0000C5�[�;�\u0000��]�\u0000�ٿ�3Xu�͆�\u0004=\u0017�p῁\u000fE�\u001f�_�ǉ�}/�REw��[�柒I\u0000=\u0005{��'~\u001d�\u0000�՗��\u0015�\u0007m�^����u,I��b\u0005K�\u0000\t\u0016��\u0000?��f�#�|;�?\u0017W\u0014�\u0016�w���s\u001f\u000fc����<E���c���\u0013�\u000e�\u0000�j���\u0000\n?�;���\u0006�����ȏ�H�?�����4�E��\u0000����ٯ;�!�?�%�\u0000�?�O;�!��%�����'~\u001d�\u0000�՗��\u0014�w���\rY��_�\u001f��j��7��h�\u0000��S�\u0000�����G�C\b�K�\u0000����C(�\u0000�K����N�;�\u0000A�/��(�\u0000��ÿ�\u001a��\u0000�¿\"?�\"��\u0000��o����\u0000\t\u0016��\u0000?��f���\u0010�\u0000���\u0000��\u0000�\u000f��Q�\u0000���\u001f��\u0000���w��V_��Q�\u0000\t߇�5e�\u0000�~D�E��\u0000����٣�\u0012\rM��l�=��?�\u0018C��_�\u0003�\u0000\u0004?�\u0019G��_��\u0000\u0004������a\u0013Z̓�z<g ����\u0000t��~\u0013�s�vy���W-�$W�W�ت1�ם\u0018��������8�1�^tb��ڿ{;\u00052i\u00040�!��[���o�.�������Dv�6O����y����\u0011撏s����ֆ����W��^P\u0007�1^cZ�(ԟW�\u0006�w!�I3\u001c�&����o�(}W\tJ���/�\u001f�X\n\u001fV�R���K�G��O�\u000f\u001bM3Z�v�\u0000�ʪn�\u001a�\n�\u001b�-���\u000b�H��i�vc��+�k�'��?Zα3�+}�~��w\u0015b~���'�V��\n(��L�0��(\u0000��(\u0000��(\u0001��������7�\u0000%cU��\u0000S_���������7�\u0000%cU��\u0000S_�xi�\u0000#\u001a���O׼5�\u0000��_������?�~��i\u001e\u001d�\u0005��\u0016�f$,�\u0014���5Y����A\u0016�\u0012B\u000f]����>�Vu��\tϖ��}��sܧ�g\u0003,\u001b�-���\u001f��\u0000���w��V_��Q�\u0000\t߇�5e�\u0000�~D�E��\u0000����٣�\u0012-O���\u0000��~W�\u0000\u0010�\u001f�\u0012�\u0000�\u001f�'���\f��\u0000A/�?]�\u0000�;���\u0006������\u0013�\u000e�\u0000�j���\u0000\n���\u0000��S�\u0000�����G�$Z���\u0000M�\u0000}�?�\u0018C��_�\u0003�\u0000\u0004?�\u0019G��_�~��\u0000�w���\rY��G�'~\u001d�\u0000�՗��\u0015�\u0011�\u0000\t\u0016��\u0000?��f��H�?�����4�0��\u0004��\u0007�\b�2��\u0004���w�\u0000��ÿ�\u001a��\u0000��N�;�\u0000A�/��+�#�\u0012-O���\u0000��\u001f��j��7��h�\u0000�a\u000f�\t�\u000f�\u0010�\u0000�e\u001f�\tq��m�\u001d\u000e�t�\rZ�Y\\�Q%\u0004�[\u0015���)E����Ɯ\u001e�Y\u0012ل�K\u001285�b:W�|K�C �G\r\u001a����-c�^%���⣆�Nv�ޖ�QE\u0015�\u0007ȅ\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005dx�é��\tkz\u0014���z���M2��\u0018�6B�w����諧9S��\u001d��|�!9S��\u001d��|�S�\u0012��G�!���)�4��?��\u0017?�_ƺ���\u0001k\u0016���O\u0003\\�L'�4{[b�\b��\u0018�ןFF\u001f�w���)��\u0012�������S9�\u0000��'K~��S\n(��s�\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\nF`�I \u0001Ԛ�<s�'��\u0000\u000f4�/��B;h����\u0013���~4~�\u001a��Z};����`��H9i\u0017�ھ�%���;��<-\u000e�z/�?#�rn\u001b�3��\u0000����'��\u001f��/ŏ�K\u000b�����.�\u0012��o\u0011ݓ�H�_\u000b|^��<W�Jy��K��K��([�#�^I�j7:���]����%��sU��\u001f!�̿&J�����ϧ����Й\u0017\u0006��:U$��N梨���$���Elxc�\u001a��5(�4�)n�%8P�q��ؿ\u0005?a�m��T��y�pN��\u0007�^�o�\u0018\f��6*z��տ�����\u0003%�͊��\"�o�|����g�~(�,Z]��\u0001\u0005��mP=Fz��\u0006?d/\f�:H�u8�X�F\u001cI2��oA^ݠ�sM�̈́vZm�v���*���*�yϸ�\u001f�^�\u0007��v[�W�G��{�������gK�����\u001b\u001ck\u0012\u0004E\n�`\u00000\u0005:�+��󠢊(\u0010QE\u0014\u0000T7���?�so�jj���<��\u0000�m��TwEGt~>x��GMw��f�\u0000��a����\u0000�t���o�\f�\u001dsa��\u000fE�\u001f�8o�C�~GQ��3�\u0017�,�ק���A�oUⴿ�Ix�����\u0000�&���� �O�ɾ$c�\u001eJ�A^��H?������3O\u0010�8\fm\\,h��ڽ���g�\u0006'\u0001����\u0014�\u001d�v~L�\u0000���\u0001��\u0000�M\u001f���c�\u0000@i�\u0000��_��d��x��\u0000|\n>�\u0007�����\u0015��M��\u0000ψ����\u0000�&b�\u0000��~�~L�\u0000���\u0001��\u0000�M\u001f���c�\u0000@i�\u0000��_��d��x��\u0000|\n>�\u0007�����\u0014�M��\u0000ψ��?�&b�\u0000��~�~L�\u0000���\u0001��\u0000�M\u001f���c�\u0000@i�\u0000��_��d��x��\u0000|\n>�\u0007�����\u0014�M��\u0000ψ��?�&b�\u0000��~�~L�\u0000���\u0001��\u0000�MjxW�w���&�\u0014�D�\u000bΡة�\u0019��T��\u0007�����\u0014\u000bXT�C\u0018#�QQ?\u00131r�����l�����\\}��͙�\u0013�?��7���\u001fg�#��V�\u0014W㳛����S����Nov\u0015�ߴ>��\u0000\b�f�vߓf~�\u0015�5���ǯ�\u001f������2!��k��0�\u0000Z�0�z9/�緐����a�����~uL�d�7����ӭ\u0013̺�?��?Z��?�z/�$\u001e2��q�̙x�\u001a�˫8ѥ)�d��\u001f��f�Ҕ��_����oA\u001e\u001d�w��\u0001��\n���k��:\u0014\u001feѬa���\n�_�����yՖ�����x���yԖ����\u0014Q\\�0QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000�?տ��k�����\u0000��������?տ��k�����\u0000�������<4�\u0000��_�����\u001a�\u0000�¯�S�k��߀��\u0016F�iv2]\"\u001c\u0012�5��ܿ�\u0004i'��P������\u000f�~��Y��\\�x�q�i�\u001f��G\u0010��ɲ�c)Ǚ��~gʟ���c�\u0000@i�\u0000��G�)/\u0018�\u0000�\u001a����7� �\u0000�1�\u0000�\u0002��A�\u0000<c�\u0000�\u0005~;�\u0000\u00117\u0017�\u0000>#����\u0000������\u001f���?���c�\u0000@i�\u0000��G�)/\u0018�\u0000�\u001a����7� �\u0000�1�\u0000�\u0002��A�\u0000<c�\u0000�\u0005\u001f�\u0013q��?{\u000f������\u001f���?���c�\u0000@i�\u0000��G�)/\u0018�\u0000�\u001a����7� �\u0000�1�\u0000�\u0002��A�\u0000<c�\u0000�\u0005\u001f�\u0013q��?{\u000f������\u001f���?���c�\u0000@i�\u0000��G�)/\u0018�\u0000�\u001a����7� �\u0000�1�\u0000�\u0002��A�\u0000<c�\u0000�\u0005\u001f�\u0013q��?{\u000f������\u001f��\u0016~�_\n��\f��R��{\u0017����#�1�k��bC\u001c_q\u0015?�\u0018�����oS;�K\u0019V6m%e�~o���3�d��cf�V^AE\u0014W�x!E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0015�|G�%烼\u0003�\u001dz��+��2�kĂi\n#lR�$\u0002x\u0000�w�23��*R�R4���K��kJ��T�(o&��z\u001ea�\u0016ދ��z3�����i�w��E��l\t\u001c\u0004P_hU,7gh%�d\u000fr�\u000b��-���|Й\"�6�k�v�T\u0007>k\rɎ��\u0003�r\u000flW�W��M<�\u0017o��/�)��\u0010��c\u0017o��/ͅ\u0014Q_<|�QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0001OV���K\u0019o/�Kkh����\u0000\u0015��ƟۃN�V}7��_]`�|\u000fʇ�ko������U��4���Uo-�������9<���\u0013�X,�\f�\u001cg��J=4������O\u0005���c���iG����\u000f�����S��\u0000Z���w<�p��J稢�~�J�\u0018*t��WE���*T��S�\u0014��-\u0010\u0001��o�_\u0003��\u00194w�#�aѬA\u0007�q�(��x�\u0019��P��\u0002-̪��\u000eq\\��\u0015�\u0014]<=_f�[]��rc�W�Qt��}�}mw���q����G�M9m4K�(@\u0003t�w1>�5����w�\u0007-������һ�\u0000�����G�������\u0000}�����\u0014�5\u001dZةJOv�g啼9����[\u0015)I�ެ�i�\u0000�����\u000e[�T���w�\u0007-������һ�\u0000�����G�������\u0000}���!�\u001b��%�#\u000f��xo�\br?Z�r�;������\u001f��|\u001d�\u0000A�o���%����\u0000��o�����w�\u0000?3�f���8o�\b�܃�!�\u001b��\u001f܏֟�\\�\u000e�\u0000�����G�._\u0007�r�����o�+������4i]�\u0000����٣�!�\u001b��%� �\u0000�g��\u0000���#���\u0017/���9m�\u0000}P>2x8�\u0006�m�p>j���һ�\u0000�����Z^\u001a�~����Eq1y&Q�ϭD�3��.O\u0010켑3��\u000b\b�<C��G�5��W��<.\u001e'\u0019V\u001d�%��y��\u0000\\��\u001a���Qe��:\u0001�\u0016���\u0015r��<��\u0000�m��~\u0006ҍF��?\u0005iF�Kk���;�\u0000��]�\u0000�ٿ�3Xu����\u001d5�����\u0000C5�_�xo�C�~G��\u001b�\u0010�_��\u0003�!�E�燾\u0017����Cm?���}��?�r�;������~JEyq\u0002��y\u0011}\u0015�\u0014��+������5�^a��\u001f\u001f����v���d~[�x}C\u001f����v���d~��\u0000���w�\u0007-���?�r�;������~Ki]�\u0000����٣�J��~f�\u0000��y�\u0000�\fp��\u0011/�\u001e�C<7�\u0004?�\u001f�?��|\u001d�\u0000A�o����\\�\u000e�\u0000�����_���W��7��h�һ�\u0000�����G�C\u001c7�\u0004K�A�\u0000\u0010�\r�\u0000A\u000f�G�O�._\u0007�r�����\u0017/���9m�\u0000}W���������\u0000}�?���\u0000��o����\u0000\u0010�\r�\u0000A\u0012���3��C�����\u0000\u000b����\u001c��\u0000���\u0000�����\u000e[�U�-��w�\u0000?3�f��+������4�1��D��\u001f�\f���\u0010��~��\u0000���w�\u0007-�����~\"x{ķ�c�u8n�6�؇�W�/�������\u0000}����\b��/|Y��,�,Q��f$s^&u�x\\�\u0001W\u0019��qZ+-Y��\\\t�ʰ\u0015q�ݷ\u0015��՟wW�?�P�u���4��*���>���Z�8m�\u0011k|P��vﱍ��L���\u0006\u001b��p�H&�\u0000\u000b~��p\u000e\u001b��P�H&�\u0000\u000b\u001f<W�~�2�[|_��u9�\u000b(\\�����y}:9^\u0016�\u001b�7��\u001a���a��������W�}\u000f��f\u001f�Xj�{ۙ5~�?[��\u001f�QB�n�\u0001�7R�\u0000���w�\u0007-������һ�\u0000�����G�������\u0000}���!�\u001b��%�#�\u001f��xo�\br?Z�r�;������\u001f��|\u001d�\u0000A�o���%����\u0000��o�����w�\u0000?3�f���8o�\b�܃�!�\u001b��\u001f܏֟�\\�\u000e�\u0000�����G�._\u0007�r�����o�+������4i]�\u0000����٣�!�\u001b��%� �\u0000�g��\u0000���#���\u0017/���9m�\u0000}Q�\u0000\u000b����\u001c��\u0000���[�J��~f�\u0000��\u001f�W��7��h�\u0000�c��\u0000��}�?�\u0019���!���h�\u0000�����\u000e[�U���嗈l\u0012�O�[�g��'C_�\u001f�W��/��k���4���\u0017���;n~X�����(��9\u0006\n8�u\\��Vk��\u0000��\u001cO��r\u001c\u001cqP��ܒ�^O��n��[�?ƿ,�i��+\u001a�����M��[�?ƿ,�i��+\u001a��������F5����\u001a�\u0000�¯�S�k��'������v?Ҿ\u0018���\u0000����.j����\u0000J�7��EW�~g��w�\u0000\":���>���+�H�U\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n���2�{_��8{y\u001e9\u000e�*\u0016���\u001bX}��� �П�>��5p\u001e���O��:�bB.�u0ی��6u�\u000fu\u001f�\u0007����\u0015����<��zYc��Pr۞?�R<��\u0007����\u001b,s�$��j��\u0002�\u0012#M�>��\u001b��=X�������\u0013�^���v��%ʶ�\u000e�-Ԗ�\u001c�m\u001cJ�N1�V��\r}K^�\u0015���1I�{���~g��Pt��Rj��_�QE\u0015�g�\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u001f;~۾\u0014�<[����F���n\u0016�]��r@���\u001d�\u0000�\u0017���\u0015u\u001f��_�L��\b\u0004{�o�\u001f��_ʿHȸ�\u0013�`�\u000e�\u0018�&��}OѲ>5�dx5��J2I�v�S�_�\u0014_���U���\u001f���}�\u0000B���\u0000~���ɏ�y��G�\u001f��_ʾ��\"v3������?�&�?�\u001e?{?%�\u0000�E����]G��Q�\u0000\n/���*�?���Z<��\u0000���Ty1�\u0000�5���\u0000����\u0000�x��?�&�?�\u001e?{?%�\u0000�E����]G��Q�\u0000\n/���*�?���Z<��\u0000���Ty1�\u0000�5���\u0000����\u0000�x��?�&�?�\u001e?{?%�\u0000�E����]G��Q�\u0000\n/���*�?���Z<��\u0000���Ty1�\u0000�5���\u0000����\u0000�x��?�&�?�\u001e?{?%�\u0000�E����]G��Q�\u0000\n/���*�?���Z<��\u0000���Ty1�\u0000�5���\u0000����\u0000�x��?�&�?�\u001e?{?%�\u0000�E����]G��Q�\u0000\n/���*�?���Z<��\u0000���Ty1�\u0000�5���\u0000����\u0000�x��?�&�?�\u001e?{?%�\u0000�E����]G��W�|\u0005�\u001b�����6����K\u0015�2M4xU\u0003ֿJ<��\u0000���T�\u0012)�E\u0007�\n������Н\u001fa\u0015̚�ޗ9�>#c1\u0014'G�Es&�w�Ă!\f)\u0018��\u0014~\u0014ۥ/k2��P�?\u0003R�_��[���[���2�'㫿\u0016k3E��BH�����.\b.pk\u001f�\u0014_���U���~�y1��_ʏ&?�濕~�O��e8(,<tVݟ���+\u0019N\n\u000b\u000f\u001d\u0015�g���(�\u001fЫ��\u0000ߪ?�E����]G��W�G�\u001f��_ʏ&?�濕i�\u0000\u0011;\u0019�\u0000@��٧�D�g�\u0003��g���(�\u001fЫ��\u0000ߪ?�E����]G��W�G�\u001f��_ʏ&?�濕\u001f�\u0013���\u000f\u001f���D�g�\u0003��g���(�\u001fЫ��\u0000ߪ?�E����]G��W�G�\u001f��_ʏ&?�濕\u001f�\u0013���\u000f\u001f���D�g�\u0003��g���(�\u001fЫ��\u0000ߪ?�E����]G��W�G�\u001f��_ʏ&?�濕\u001f�\u0013���\u000f\u001f���D�g�\u0003��g���(�\u001fЫ��\u0000ߪ?�E����]G��W�G�\u001f��_ʏ&?�濕\u001f�\u0013���\u000f\u001f���D�g�\u0003��g���(�\u001fЫ��\u0000ߪ�W� �}�x+�ګkZt�\u0017s�e\u0012e�ۊ�Oɏ�y��N\n\u0014`\u0000\u0007�x\u0019�\u001cb��\u001c�U)F)����x9�\u001bⳬ\u001c�u)F)����l�c��F⠐\u0007z�������\u001e,���jv�\u001a��\t��:ǐG�~�S\f(z��¼\u001e\u001e�\n�=^u�SSrV������{?����^�5'%mo�����\u0000�\u0017���\u0015u\u001f��G�(�\u001fЫ��\u0000ߪ�h�c�\u0000�k�Q���\u0000<�����\u0000����\u0000�x���������\u0007�����Q~>�\u0000�WQ�\u0000�T���\n�����֏&?�濕\u001eL��*?�'c?�\u001e?{\u000f�����\u0007�����Q~>�\u0000�WQ�\u0000�T���\n�����֏&?�濕\u001eL��*?�'c?�\u001e?{\u000f�����\u0007�����Q~>�\u0000�WQ�\u0000�T���\n�����֏&?�濕\u001eL��*?�'c?�\u001e?{\u000f�����\u0007�����Q~>�\u0000�WQ�\u0000�T���\n�����֏&?�濕\u001eL��*?�'c?�\u001e?{\u000f�����\u0007�����Q~>�\u0000�WQ�\u0000�U�\u0011�&h\u001a���\f�V:���7hϺ\u0019F\u0018|��\u001eL��*r�Q�\u0000\u001e��g�8�\u0011��V\u0016�%\u0014�wW��>k?�\u001cF}�XZ��Ri�_���q��{�~p~П\b�e�|LԮ�|;{sl���8�\u000f&�Hi�$c��O��\u001f����?^U�AI�[[������\\���҂�����\u000f�o�Q~>�\u0000�WQ�\u0000�U�?�C��w�:\u000e�\u001e��O�;�J��\u0004�+�\u001f&?�濕9QS��>���:��Nu��\u000e�\u0018�;j��}\u000es�\u0018��\u0007,\u001dJ1�v�7�Z(��4?5\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n��ګY��g�\u001a]YJ\"��RرP߻�T�A����=���z�x7���{\r\u0013�6��]H�u�I\r���\u0012\u0019�d��z\u0001�\u000fZ�r\nN�m���{ԅ��s&�V���r\u001aN�m����R\u0017^\\��\u0000+nx��\u0013�+S}�9\u001a�5�\u0011۪Z���2[s���\bQ�\u001f0�8����_�'w���\u0012�\u0000�\u001f�\u0000k�_}W���93����������y\u000e\\����/�\u0000%_�\u0014QE~z~|\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0015���\u0014*�Y~\u0018�7j\u0013ɇS�ܖ\u0001�h�\u0018\u001bI#�9�\fq�g��+�\u001f�(��-m�{P�Ώw+&\u000f\nD`\u001f�O�_k�t�L�\u0000\f�F��\u0016ϴ��n�}�K�o��g���\u001a�֓��J���\u001b(/���u��g]��\u000eFX�\u001b}����u~I�\n֭<=��������-�(ZGU,@ݎ���l���.�&eJ�_\u0014;uM���_��>%P�̩VK��n���F�\u0000��+�\u0003� ��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��\u001f���i�0�Z��I\f\u0016\u0011���ܱ��~]�i<\u001eB���?����^��N�W�}~�K��M�K\r�H\u0014��4\n�g�\b<���\u001b�u3�T����Z_.��^\u001c�s�%R�F\u000f�i/N��X������`�ʑd�I\u0001�s��k�3�ן�\u001e\u0019�.��\u000f�g\f�Z�B�@q���{��m~�~�\u001e2�\u0000��৆5\t.��u\u0015�������$)\u0018�\u001c\u00009\u001cW�������lBZFM?����ϰ�7\u000f)ap�����5u�3�袊�z?�B�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�\u001f�&j�[���K�\u0002�\t��o%\u0019�/�F2ē������\u0010��O��#��.^�;[\u0019\\O\u0018b��HR6���t��)���i%��Idb��rX��I����/�?��K�݊�[�\u000f�|1�?��K�݊�[�\u0006W��\u0000�O�\u0019\rSᾧ�ր#�WfE�0;�^y\u0019� ��\u0015�\u0005}G�\u0000\u0004��#��\u00135�! ��+ �c�H�F��fi\u0017\u0003�\u0003\n�Ia�\u0002k�x�\b�y\u0015n������6}�\u001ba\u0016/#��\u0016��=\u0006��*(�����ࢊ(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0003��\u0000m/\u0012������p�\nK�I\u0015�Iq�Fo�h�\\\u000f¿3����(���i�\u0010�~ϓ$�_y��m\u00016���y�{Wĕ�K��\u0013��$j5�IJ_�o�Qx}���I\u001a�kRR����\u0005z�����\u0007�p�ơ{|�\u0016\u001ek�q\"��+F�+\u0001��}�z�^[N�W�D�7h�B\u0019]N\n�Ѓ_�c0��a�a�m8���h��f\u001a8�5L4��\\_�4~�)\f��A新|\u0007��?\u001bx7G״��K;�d�%����\u0004wS��A\u0018 �A;��=R��NT��ӳ^h�#�NT�*sViٯ4\u0014QEff\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QL�O*\u0019\u001f��M\u000bQ�O��ۃ�m�\u001f�w�*gXt{h�<�\u001f)��1�\u0006x�u\u0007�oҼ\u0002�|k���|_��/!����r\u0019��\f䏔�c�8��L�Ư���\u0006��\u0005\f*�\u0011K�m\u0013�W)��\u0006\u0002�\u0015}��󶿈QE\u0015�\u001e��=�\n���]�\u001fi��\u0014���w\u0013A;ȿ#�%y������\u0004{��\u001e�\u0003�\u0000�~xٴ��\u001a��K��\u0016�\u0002�\f��Gx\u0003���\u0007\u00123\u0012ݓ\u0003�_~W�7\u001a`~��WKi�u�\u0000oj�\u0000�k��\\e���w]-�������\u0000ɮ\u0014QE|A�!E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001^I�V��o\t�\b�U�PAp�V�O�&���g�;�\u0000�e.\u001bo\u0019\u0001���n�)�\u0000��x��g�׃��쌟�ү��\u0017\u0006H�;��\u001eg\u0018���\u001fW¸\u0007��\u0018z=\u0014���u����l\u0003�3�=\u001e��?H��\u0000+\u001f\u0018QE\u0015��`\u0005\u0014Q@\u001d���\u001cK��⿆��i\u0004p]�s�H��\u000b��(\r�J�3�3�\u0015��_�h�\u001b\u0006V*�r\b8 ������\t~\"|!�o%��f�o\u0002�^�F\u0000H�\u0000\u0012~��\u0014�\t��_�x��7\u001a\u0019�\u0016ׄ�8��y�o�ysq��Amx�������E\u0014W����E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001_�\u001f�����7�?\u0012����֖S}�%��iB\u0014�\u0000X#�6�̛�(�\u001b�\u000e��?�C�\t�\u001f�� �\u000b�\r��ʄ&�\u0000�\u0018N;��s�_��W/yu5Ę2J��\u0003\u0003$����\u0018�\u001c�W��d�W����/����<\u0003�j��l���z��%��QE\u0015�\u0002~�\u0014QE\u0000\u0015���\u0013����x�[���2^E��w��\u0000&\u0001\u000b\u0010R��%�)�\u0000�o����\r�\u0016o�\u001f\u0014�-q%X���ow��L\u000eB�N\u000f\u0000|�v�s��\u000f2ʱ\u0018X���OU��Q��E�y�U_\r\u0015y8���_�?Y��l�`�m!���.-�A$r���Ԍ�\b�\rM_�m4���v�vaE\u0014R\u0010QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0001�w�\u0014\u0017�k�x'F��N�~�q����n\u0011GІ\u001f/,pAɯ����\u0000kO\u001b\u001f\u0019�m׌W�]�i�\u000b;}ҖD�>p�\u0003o͐G��^9_��#��\u0000fd�i?�K���_�Y|���\u0012˿�rz4��%��e�ାAE\u0014W؟`\u0014QE\u0000\u0014QE\u0000~�~ɿ\u0013#���wL��<w�F�*��`�l�Ƈ�R;2��@�$s��c����+��x[�Z��5-J;]/Y�\u001a�)��עDDT\u0019�.�����9��@��\u000f����f�i�6����=��t#�vW���U�\u0015hKޏ��\u0000't\u0014QE|Y��E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001^}���\u0015����:��-\u00025ݪ\"²F]K��\u0000@u#���:��\u0007�k�O�(��-����� �Isn%�.�3��6\u0012,��I8��\u000b\u0001�\u0010\u0018���\u0018�Vk�P�I^7���\u001d]�v��Q�9j�sj8i+�������o���������wR��3���+���\u0012K\u0013�I&�����I%da$��\n(��(�\u0002�(�\r/\fx��\"�5�\u0007\t{���u\u000b2�\u0001у\u0003���\u000e������\u0016_\u0011<\r�k�3K<w\u0010&�%��&@�x�T6\u001b#*6�\u001ct��:���\t��׿�u�\u000b�^�M%�[�x�o\u001eE�<��\u0018��E�$��$q޿&�\u0017*�+.X�/z���-�����?(�\u000f*X��c���O�\u0000%z?�����TQE4\u001f�aE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0005mSR�Ѵ۽B�Q\u0005��/<ҐN�PY�\u0007'\u0000\u001e��'��\f�\u0014~$k�'�\u0004B�|�\u001f\u001f$J\u0002F��2B*�{�5�����B\u001f\r|6o\u000b[\\Y���0I��f3$\n����\u0006Y@�\u0011�\u0000������\r��a����^����\u0000�n�o�?�|8�=�\u001e�gQ{��c�\u0015����(������(��\u0000(��\u0000(��\u0000+��9�\u001a��_�M\u001f�v��v򅸌�H[�_˟�\u0015�QXb(S�ѝ\n���i�&a^�<M)P��\u0019&��g����w�p]E�*h�D�0pFEM_2~�?\u0014���\u000fn�-t�/}����SK�,���cU�+�i\\t�\\\u001ep>�����-�������\u0007�����3��6˪eX��*����t�j�(���\u000f (��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000*\u000b��m6�k�ˈ�maR�O;�DQԳ\u001e\u0000�5=x��k�*\u001f�_\u00075m�:�Z��:�F�\u001c3���\u0000�j�<�8�y�C/���1t�����__�硗�������Wsi}�\u0000�����?�>?�_\u0016�[�]�M�?b�e\u0003�D$\u0017$u���x�y=\u0014W��\u000b\tO\u0001������$�����a)�p���~\u0018$��(���;\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u000fB�\u0007�:O�\u001f\u0014t=q���1.\u0004w�D�\u0004���1*\u000f�T9`\u000fu\u0015�Ĭ\u001dC)\f�d\u0011Њ�[��?�g�s����֍s=Ʃ�L���\u00133�aw1#hB0\u0000\u0000m�M~+�FM��C5����/����M����[�l��Q�iMk\u000fv^���M��v>���+���}\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n����>'��'�\u0015���˥h���n�!d����\"���$\u0002>����7����>\u0019�$���A.��\u0007�a�I�:#�\t%U\u001c����\u0016R}\u000f�-~���K���Wx��\u0000n��~���M���Wx��\u0000n��\u0014QE~�~�\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0015��\u0013��?�O��W�!�;���S� <��k�\u001d�N+����\u0018zx�3��W��My3�\u0011����:\u0015��$�^L�����k�}\u000e�V���KȖh����OL�գ_(~�\u001f\u0019���1'��\u0019ݵM-Zk-�H{\\����*�\u00068�������e�e�2�}\\\u001dE��<������s�T�1�pu\u0017���]\u001f�\u0014QEx��\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0015\u0015���[M;�dH]��\u0000g�T�������_�>\f�@����[�\u0010�\u001a]\u0006ڶ�\f\u0007a���p\u0000t��\u000f�����\\e<\u001d\u0005yI�\u001d_�jz�^_[4�S��W����%��\u000f�C��|a��5��+\u0016��!��;Hw@Ė|�,O\u001d��h����8:Y~\u001a\u0018J\nт������\u0016\u000e�_��\u0016��`���0��+��\n(��\n(��\n(��\n(��\n(��\n(��6�\u0019�-[�^$��4[�-/m%Y\u0006�\u0019V@\u00181���Y\u001b\u0018+�E~�|6���|P𝞽�\\���\"y��\u0005��(��>2\u0003��\b��\u001a���\u001b��?�|_\u001f���Q��\u0012�[����\u0005\nr\u0001$0@���\r~_Ǚ\u000f��\u0007딗�(��c�_-�Ϲ��\u001d�?�x\u001f�R_������|�_3�\n�(�����(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000��k\u0016^\u001f�n�-F�++\u001bX�Y�&`�\u001a��$����o�ڗ�?\u001c�>\"��2�;\u0004�v�X�Q�\n��g\u001f1P�nf����o\u000f�\u001fi�\u001f��%�In��Y�X0.\u0018\u0018�n8*Wq\u0000�*\u000e\n�ƕ�%��B�8W�W^�_�uQ�\u0000���H����!x,+�k�~�»G�\u0000��� ��+������(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000�V(��*GB)(�\u000f�?�G㥗�\u0003[i����:=�Cwm\u0012>�,|�ɹ�2�y\u0000�W�W��\u001f�\u001a���\u0018���Q2�\u0005'�i\n�r�\u001f���p\n�\\���4�\u0000\u0017x~�Y��⽱��K\u001c�6U��}A� �\b ���\u001b���>7�\u0014#j55^O��W��?��ׇ����ބsSU����yz3R�(�͏�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002������\u0007�χW���j���+N��Vt�o��R\t\u0018�<�W������s���\u001d��\bd�iX*\"��Ğ�\u0001_�_�����\u0000��8�C(]\u0012�I-�`����\u001d��\u0007��v���\u0010��g���\u0017����ϴ~}|�}�\b����r���T����?>�W<�P��R����\u001el�4���X�q��\u0014Q_֩(�#��%\u0015d\u0014QE1�\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005}_�\u0013~���:�o\u0004x��\u0000��N���\u0012\u001b)F�t%����\u0018<8�|䏔)Q�6\f��)� ��^6o�P�ps��\u0016���Mlך�U����|��q��\u000f\u0010��Ϫ}\u001a��U������\u000b�L��m�+�N=\u001bP�G�M&\u0004�Q$�k�\u0003\u001ej�I8\u0000\u0006'�5���w�e���T�x�iE����g��c����S�b\u0015�\u0017��kɅ\u0014Q^a��\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014W�~ѿ\u001c��\tx%�b\u0010�k�Gʱ�����d#�U�����\u001e\u000e�?\u0011\f.\u001e7�����w;0x:��D0�x�rvK��O\f���\u0000i\u001bt���u���\u001a񜦵w\u0003\u0000�\u001e\b6��%� �\b�\u001bNw0_�*Υ���������qus#K,�1fvbI$�O&�W�\u001eE�P��Q�Q�y>�]_�vG��E�P��Q���y>�]_�y\u0005\u0014Q_B}\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0001�|3����0����-*W�{i\u0007��@��'���\u0011�\u001ct��_�\n~,��\u000f�\u0006�����\u0014q\r�3D��M�X�r0H\f9RG�~FW��̟�\u001d��/\u0014�wM%φu\u0016D��.v�w�n\u0015@$��a���\u0019�1��\u0019��ΰ�Y����ZyuO���?7�.\u0019Y�\u001b�8x��\u000bO�.����?O���\u0000\u000fk�^(��5}:a=��\tq\f������}GcZ\u0015��(�\u0012q��G���(I�J�\u0005\u0014QR@QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE2YR\b�Y]c�\u0014�;�\u0005\u0003�'��q�bx��:/ß\r]�� �6Z]��$�&���*��\t��?\u001ek���w�\rW�/��u��O��f���n�\u0004\u001b�ь���O'���\u0000j/�z��\u0006�&��<�^\u000f������|��$����������\u0001_Ӽ\u0011���\u0014~�������X��I>��e�����\u0017�ɣ��\\=��Ƿ��]v��\u0014QE~�~�\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000}]�\u0016~�I����\u000b�I�*��}���y\u00131\u0000�30\u0001\u000e??�}�_�]+�?ػ��>*�O\u0003��Ri��8�'�|�0���/���\u0007�%Gr\r~\u0013ǜ+~l�\u0005\u001f���K�\u0000n������\nߛ7�G�i�K�\u0000n���YQE\u0015�)�@QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000W�\u001f�o�1\u000bZ]�>���ܤ��R�`�d\\g>J\u0015'\u0007#��=�k����?/ï\u000b��t-X[��P\\2�\u001bͷ��<�\"���?t���Lr?;��[���i\u001ei�b�$�Y���$�����o\u0002p��8������E�k�z.��|\u000bª��m�^�~�_V�ע�2�(��3�\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000*k+ۍ:�;�K�mn#9I�r��؎ECE\u0002j�3�w�\\��-�.Z&���[��%$m\\-�˱dP0�\u0010(9<���E~0���\u001a]�\u0017v��n!q\":� �W������\u000f�~\u000bG���/\u0013�~���\u0012Aa�e\nz\u0006�\u0019\u0000�g�6q�\t,�O1���I���[����=6j��\u001ck�k-��pK�R~��V�u�\u000fM����E\u0015�\u0011� QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000W����\u0000�v��w�w��7����H��v\f����\u001ed��\u0000\u0001 \u0013�v������~37�O��k6q��j�ʐY��HB�'��\bf\n9 \u0011�\u0015����\u0014�\u001e5�&��견څ��<Ϊ\u0015w\u0013�\u000e��S��\u0012�ؗױ���3V��=���Ը7��\u0000�%��_�b�_�մ�\u0000\u000f~�\"������V��5K�o�\u000b�\f��L۝��&�QEM�1�Tb���/\u0018�%\u0018�$\u0014QEQAE\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001[�\b�����Ėz��x�Z��eXr��ч�)�+\n�Υ8V��Q^/F��\u0019ԧ\n�t�+���٣�G�\u0007��\u001b㏆��nV�]�P/��l�g����\u001eǷC�������\u001b�?\u000f<Ig��W�e�Z��u�ú���pA��O�?\u001f�o�>\u001a\u0017\u0016�,��U\u0002�\u0000L-�m����\u001eǷC�����!<�o\u0019�M�|\u001fg�����o����Fy<�/\b�A��}��g�z��R�(��\u000f�B�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002����\u0017�/�~\u0013�[֦˜���dy�Rc�Q�d�\u0003���w����okZ�ۜ�-l�#ͺ�\u001c\"���\u0000�\u0001�����c]������r}�~K{T'ʶ�<\"\u000fOSԞM~��\\'W=����4\"�}d�/���?C�>\u0014������\u001a\u0011z��}���z�������\u0000\u0015ϭ��䜭��\u0013�[G�\u0011\u0007�=I�6�+���\nXZQ�F*1��Kd��\u001a\u0014)a�F�\u0018��*�-�\n(��7\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n����u�\u0002k�k\u001a\u0006�6��B\bI�#8#\u0004\u0010r\b>�\u0011X�Vu)¬\u001d:�8�\u001az���\u0013�\n�p��OF�����\u001f\u0000?i�\u000e�h���e6\u001e'��Is���dd3F��8\u0004��\u0018g�{-~0�j\u0017:]�WV��oq\u0019�I\u0013\u0015a���\"���j]3�\r��������h|�\u00126���G2�\u0003\u000bzdt�o��\n�Y|n\\��u[�y��������\u0016�\\���r��K�����?�W���(��#?%\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n�/�\u001f\u001f�;�Z�$�\u000b]޾ݶV�<�\u001d&1�\u0007�Y�d�by�\u001f�\u0017���~\u0007�\u001d�p���Iмv\u000b&ՁH;d��\u0019�\u0017�\u0019�u��/\u001b��Y���[�{]�{�F����\u0014vE\u001f p\u0000�ԸO�*��b��ƇN�������~�\u001bW7k\u0017�N4:w�����}M_��\u0000\u0015�ߋ�+�\\�'�9K{T'ʶ�<\"\u000f�z��q�Q_��(R�ҍ\n\u0011Q�U�[$JP�K\rJ4h�F1VItAE\u0014V��E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001O����x��G�h�:I\u001b\u0015d`r\b#�\u0007�2�M_F&��>���?lK_\u0016�i��\u001b\\Gg�ƛ\"զ�R+��\u0015\u0015�x���0v��J��)Rx�H�d��et9\f\u000fB\u000fq_������]��Z��6�k�\t�Ag�I��h\n�ޱ�\u0001��ֿ\b��\u0004IO\u001f����~.?�����/��\u0015%<vT��?7\u001f�G��}�ER���;�\u0016+{�_��vlJ�Ŝ�,d�\b\f��*�~\u0013(�7\u0019+4~\u0017(��\u0019+4\u0014QEI!E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0015_P�-t�)�/�a���w�=ā#E�f'\u0000}i����\u001aNN�r�|��D��:w�\u000b��\u001f\u000e-���=�1�I7Eg!+�~8o��`\u001e˞\u000eG�~��-����\u0015�~dI����\u000eW��\u0018�'\u0007�ߗ�|__�p�\u0002{t�ٴm\u001e�z7�.�yu����\u000b����ѴzA�ߜ���ׯgw[���G�]ꚥܷڅ܆Y�&l���I�\u00008�TQ_��1�Tb����b��b��QE\u0015E\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u001e��>�Ժ�\u0000�9c�%�j�\u0015�q$�2g̀\u001c�h\u001b )9\u0004��8�\u0012KW���߉>\u001d���\rg�Z�j\u0016[�LB�x�uWF�S��9\u0004\u001a��������\u0010|-�\r���_�m$n\u001aH7\u001f*p26��a�G�x��������6'\u000bju�\u0000\t���|�~k��\u0017��9�8_r��/_?5��O׺+�?g�ګD�Ο���\u000e��@p�\r.�p\u0000�h�\u001d\u0007�9�׹��^?/�e��\u001b\u0017\u0007\u0019����ך?���~'-��ظ8�WOf��QE\u0015��xQE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QE\u0014\u0000QEyG�/�7�_\u0004�|��7���3��������I�ߵv`�x�}h���r��/��;0x<F>�p�h9M�������/�:/�?\u000b�k���[Z��Q\u000b��ā\u0019�Q� \u0017`�\u0003<����?�P��bԟE�^[/\u0007[I�Fr�|��,���\u0000u;u<��\u0007�\u000f��%�˯��\\�Vy\u001eF�\u000b���\u0006q���1��<������n\t��r����u�h�wk������~\n��������>����w\n(��R?P\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��'���ү`������\u0007\u0012E<,Uс� ��W������\u0013���7�Թ���dV���+5�@\"*I\u0018\u0000��\u0019����0{|�Ex��M��h:\u0018�]t}W���\\�s\\�\u0005��t1�����G����'��\u0011��-�-5}\u001e�+�6�1$7\u0010��\u0003��b\u000f �kJ�'�\u0011|z�g��G��oL�\u000f��M�b��2\t!s��\u001fx~��\u0001�G����ƹ\r���L�R3+��x��\u0012\t��>\u0000\u0004��\u0007�_͜C����ʵ%�(�\u00002�/�.��z\u001f��C��ܕʵ5�(�\u00002�/�/�oC�(������(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000(��\u0000*���k�Z�syq\u0015��H�I,�\u0015Q@�bO@\u0007z�\u001f�-�N�\u00195��}B�Y���`\u001aY@\u0007�������\u001a�����H���N���\u001an�\u0003H-lm�;\u0018������\u000foj��\u001e�\fv{%Rܔ���\u0000\n��y�>���G\u001d�IT�%\u001f�}º�^g��{��m>��7�g�[�|O��ہ\u0012�\u0001+\n?,I%K:�\u0000;Cn\f�\u0017�Z���tno�ک����j��2{\u0000\u0000\u001fJ�EJ��\u000e\u0007#���p��'����\u0015���%��X\u001c����CW���~��V^AE\u0014WП@\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0015-���7\t=��[Μ��1V_�\u0015\u0015\u0014�MY��ՙ����ۢ�Öqh�\u0010#���\u000e|�f&\u000f<j{H���{��;7\u0002���_�|;�\u000fH]O�zŮ�dp\u0019��-\u0019#;]O̍�\u000e�\u0000�ҿ\u001e+��?�\u001d�޳\u0006���w62G4SI\fS:Eq���IUXoN��؟Z��>��\u0000\u0005�9W��eQ�o��]>Zy\u001f���\u0003��\u001c��_�����.�-<��:+参\u001f�&��K�������w~R\b��Rm��\f0 ����\u0006O�}~�����\u0004��d�\u0017\u0019I\"`���\u0011ֿ��<�\u001b���8�n/�T�\u001aџ��yF7(��q��_N��5�%��+�<p��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000��(\u0000����#;�DQ�f8\u0000z���������\u0007=ޝᨿ��Xf�,�A�e\f� ,\u000erW�A�p�8#����8�گ��Sr}{/W�=l�*�f�}�\u000e����z���O��M��KJ�S��+]+O�����#@OA�Ԟ�u=��ό��̩sq�|;���S��^FI~�1��`u\u0019ps���b������\u0015�\u0003s�Mbkȃ���\u000e�hyb6F8�\fF���\u0004��+�����&\nճ6���~��e�����!��\u000b��lͪ��_��Y|��/kz���=J}CT����wg�{�.�I$�}�?�Q���v1�\"�\u0015d���\u0018�(�Y ��*�\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n(��\n�?�ߴ��~\rJ��wK}��A�N���p\b\u001by�u\u001fw\u001d+�(�<^\u000f\u000f���b��\u0007ќx�\u001e\u001f\u001dI���N/�?J>\u0011��~\u000b��w�\u001dA�º�E���g\u001e\\�L��d�Q�T?1\u0004�6�q�����^��������C\r���u]\u0011\b\u0007J�I�%\\�#l�;rrT��\u0019߆���e3��%��[���Q��u��ez�L���m���\u0000'T~�Q^\u0005�o����鍎���_WgT���\\��X��&\u0002��vP�H\\�g\u0003�`���7�*J��F\f:g��\u001f�~)��q�eWG\u0019M�^�������n/-�����K��{?�%\u0014Q^i��\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0015\u001d��V���ʐĜ��0U\u001fRk�~&�֟\u000f~\u001b�4m��������Y\u0012�u`\u0018;gjc=�88�+�\u0007��f\u0015\u0015,%79y+���g~\u000f\u0001���T�����������^3�����o�3�F��\\֕�$�le\u0005��I��\u0001U��*\u0015'p\u000f�\u0007\u0018?\u0019�Z���w�5f����\u0000�cD�\u00156Zl�I\"��$��a�\u0018\u001bT��\rxa$���_���\u001b�Jټ�\u0000�����\u0015�O�r_\u000e\u001e�si�\u0000ۑ�e�_y��\u0016?i\u001a�[6��7���v��k��D�Y����aH^{\u000fRk�h��n�`��\nJ�\u0016\n\u0011]\u0012?k�`��\u001aJ�\u0016\n\u0011]\u0010QE\u0015�v\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005z?��\u0000�\u0007ƿ\t�L�>�$��2��7ğL\u0000����\u0000\u0002:~\u0015�\u0014W.'\u000bC\u0019M��AN/�W9q8Z\u0018�n�\"\nQ}\u001a�������A�\r�\u0016\u001e0��\u001dwW-���%��ʩ\\\u0016\u0019\u001d��\u001e�\u001fMx{�\u001aG���/�}F�Q��$�$��7���H�3��=Ԏ���un�OǞ#�5�����}���+5����\u001d�X\u0003�\u0019�\u0007���7��\u0005��L�~�]���~>��Y��8,M�e��R�����������\u0007�y�\u0000\u0005\u0001�6�n��-���\u0010Q3\u001b�\n�LĮbR�6\u0000\u0018\u0010H\u0019�g\u0004�\u001bꟆ�����\u0000�F84�r8u#\u001a�i���2�����9\\\u001c�,\u0007�#?�f�'��)ʽ+�}�����_4��sN\u0014Ͳ��^����}�����G��H�\u001dC)\f�d\u0011���ȟ\"\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014QE\u0000\u0014W\u0007�?��\u0001�\b�]o�:}�ͰS%�r�n>b1��,z����J��Ɵ�Q+��f�\u0015[[�\u0004%��?�#��\u0003� \u0019;6�_\u0001�\u0018`2�Q���m�k���t���_7���\u0000�>�-���5�\rE����V�o��\u0000\u0013�-KT�Ѭ���.౳�\u0003%�̋\u001ci���b\u0000�����_\u0014�n\b�B;�?\u000f[��\u001db)%��\u0016�\u0019\u001d�qpN�J\u0006\u001bz���P>\u001a���_\u0017|F�2���\u0017����,3JD1����aTp8\u0000t�V�`�|6�P�Lʧ��\u001b������)��\rB�3*���\u0000,t�߻�\u000fR���Ix���א�:��h�\f�i\u0016��\u0017oL�ny�ז�E~�����4�\f,\u0014\"�%o�w��?Y�`��\u001aJ�\u001a\n\u0011]\u0012��;��(���;\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u000fU�o�N�A�aoqo�j���`�C�n�X��\r�o��08���\u001c�\u0000�A�����4�e���������G�E(NI\u001fw#�����W��\\+�f��z)I���������f<-�fw�z)I����\u0000\u000f�����5x'�$q�\u0000`����w�>��\b�\fFv�l\u0012@���m_���%��$R4R)ʺ\u0012\b�\u0011^��?�o�7�.�Z�ėW�v谮��9���\b;v��~�2� \u0013�3_�f\u001e\u0019M^Y}{�M~����3\u000f\f��,�����U�G��\u0015�����(M��\u0011[x�@}M�Q�_�Ҥl��Q��T\u0006l�c�\u001f{�\u0000\u0005{ׇ?l/�\u001e\"�i��&]2h���[]J�Hd@�P\u001c\u0015w�Df'�k��\tgY|�S\u000f).����v�i\u001f�c�O9��j�w%�>��.��#�誺~�e���sey\u0005������\u0004��D#!���#���_$�����n..�j\u0014QE\"B�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�(�\u0002�)�M\u001c_~EO��(�v��+�<K�a|(��3\u0013�e�.#We��m䙥*��U�\u0010\u0012T�s\u0000A\f\u000e�\u0004���࢖�.\"𯄦��_&�X� \r��t1�#\u0019\u0003\u0012\u000f_j��\u001f\ngX���4��%ʿ�k~\u0017>�\u0007¹�9��\r$��r���߁�Ur>0����\u0000�`�\u000f�����,�\u0019���Āv��pk����\u0000�_�/\u0015���ŗv�\u0018e٧\u0005�\f\u001b\u0019\r偻�\u0019�2}Mye������\u0013I<���\u0018�������5[�a]%�\u001a�-/��\u0013\u0001��V��\r\u0016���\u0000\u0007��\u0000\u001d�\u0000�A|7�#��]\u001a�Y�j����\u0011\u0006߆\u0004r��\u0019\u0004w\"�t���{�'�Bh?�?�,dܿf���%Kd\u0002�\u0000{#��Ex�\u0015�n]�\u00196YiS��%�^��t_$����\u0011���J�\u0015).������!]�Wgv.�r��$�SIE\u0015�G؅\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u0005\u0014Q@\u00174�oQ���^�w�Zm�\u0002\u0016��f�E\u0004`��A�W��[������t}f\rf2�\u001a.�l����\u0014�I=�&�:��q�f\u000b0V�ь�R���qyn\u000b\u001e���\u0019���\u0000\u001dϲ<\u000f�\u0000\u0005\u000f���a�w����\u001b7ZT�\u000b��?v�\u0000\u0005��\u001eG�\u001e��~��\u0000\f�kx\r����r����[\u0016\u0011�\t�u���1܊�ޢ�/\u0017�\u0019\u001e)�F\u000e�������|n/��LKr�\u001c\u001b�W�������ÿ\u001b|\u0007��\u0019�<W�\\\u0017\u000eB����ٻ��O1??c]|w�Ҙ�\\D�Bʛ\\\u001d�r\u0018\u000f\\`��\u0015��\tR\b8#���'�� ���o�5��[�W2C,w\r���$s�rs�����_M��ĵ�(��T��|�'�\u001ao\\6%�)F����#�.����?jߊzdh���ˀ�\t3s�\t���I\u001d?v\u0006=\u0019��\u001a��=�|�EҒq���Z�9\u0005\u001a�����9\u0003�+���W�W��8��NP�ͧ��~'����7��NP�ͧ��~'��\u0015�\u0016��\u0000\u0005\u0017��?���6������h��ǟ�7\u0018�㟥u�\u000f�\u0014;�W@k�oUӏϟ��w=6��S�_>�G]�x5�'?�{��^N/���xU�+>�{��^N/���}]E|���ݟ\u000b���,���߷e͗8ʍ�#7\u001c����:gj����Gqc\u001d�����d\u000em����\u0010���!\\����^L�s9����?�\u0016�\u0000$yS��➒�T�\u0000�[���tW�h?�\u000fß\u0010h���^4�-c��H ��!�x�Uј\u0015#�\u0000Ց�_�\u0000�������\f�\u0000����\u0000��6Yv6\u0012q�\u0019&���\u0000��e�c!'\u0019Q�k����ʊ�4?�>\u0011�5����)�u[�R���Q�i\b\u001dN�bp+��J��Q�-H��5c��*�_-H��Ղ�+��g�\n�\u0018ľ!�\u000e���.�.+��I\u001c3\u0004\f\u0010�����\u0003�H\u0000�)R�ZJ\u0014���D�*���J.M�J����\u001e\u000f�\u000en%��<u����\bܾ�\n\u0002J�|��\f0Õ��Fr�\b�\u001f�\r��<��s�2d�[�\u0011��\t��I�\u000fn�\u001dH�Z˱���2��_�\u001dk.Ʒʨ��\u0000��w�W�\\~�_\n �xWY��\u0015��㱓c\f�22\u0001��\u0018���������n�����d��.\u001c\u0005>DV_9�\u001c|�\u0007\u00199��N3�}H��s+[\t=��N<7�J��O_���J+��c�\n\u000f�;}:i4�\u001b[��\\yv�\u0011�\u0002?#9p�F\u0006O�=1�\\���\u0014n\u0016�qk�i\u0012��\u001amD2�{�\u0018==�Х���ex���q_�L�)pn}Y^8f�\\W��>΢�=�I�\u0000\u0005\u0000���n�iz~�����g�&��s��䯧8\u001d+��?l\u000f���{\u001f��f6\u0014͌)\u0001���ʎ�.3�H�^�\u000f\u000e3��u\u001c!���k�=�\u001e\u001c�\u0015l�8Cն�\u0000\u0004��~�����\u001f1<�����v��8��s�!���?\nZ��j�#�lc�`�\t.Wr6��*\u000es�:W�\u000e��\u001f�>#�\u001bRԼC���2\b��ܶ⣢�\u001e��4�\\���#K+���If'�$�5��\u000b�O\u0013��Q�߫��G�a�1�<F+�F?~���#��Z���\u0016�\"E�S��%TfU��fW �\u0017wA�~D\u001a��w�\n,��h�\u000fi\u0013q����v�\\\u001c(<���\u0005�8�����/��\u001e\u001fZ��O�I�\u0000��>�\u000b��I�֤%S�R�m�t�mo���L�k6�i3\u0019w��  m\u0003`߻��>�'�q^I����\u001e)�G�u�CT2\u0010X]ܼ���x'\u0003\u001b�\u0003�㎵�E}�\u0013*�`�hF\u001e�I���g���8\u001f�j\u0011��R~�E\u0014W�z�E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0001E\u0014P\u0007��\r\n--edbc727e-815d-4ab4-a3a6-2275aa698810--\r\n"
		payload.encode('utf-8')
		headers = {
		    'content-type': "multipart/form-data; boundary=edbc727e-815d-4ab4-a3a6-2275aa698810",
		    'content-length': "51272",
		    'host': "api.kard.eu",
		    'connection': "Keep-Alive",
		    'accept-encoding': "gzip",
		    'user-agent': "okhttp/4.7.2",
		    'vendoridentifier': "android:23913bb9-ffea-48e3-bdf4-24c9c1f70fd9",
		    'authorization': "Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NjRmYzU3Ni1jNTRiLTRiMDktOGQ0Ni1lZGQ5ZTcyNzRmZTQiLCJzdWIiOiI5YWM4N2U4Ny1iMjMxLTQ0ZjAtOTk4MC00ODFhODliOGI0NGMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MTQ5ODQzMDAsImV4cCI6MTYxNTU4OTEwMH0.figL7jECaFIFWYnOkrqmt-_pL5HJugZ7ITu65THzy7A",
		    'accept-language': "en"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)

		print(response.text)
		'''
		raise Exception('This function is not yet usable. any help is welcome, open issue or make a pull request :p')


	'''
		Get informations about Friends
	'''	
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

		#Send money to friend
		def send():
			raise Exception('Command not set. I need to get friends in Kard before lol')


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
