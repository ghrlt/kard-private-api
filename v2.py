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
			"host": "api.kard.eu",
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
	def id(self):
		payload = {
			"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { id }",
			"variables":{},
			"extensions":{}
		}
		r = self.s.post(self.api_host, json=payload).json()

		return r['data']['me']['id']





k = Kard()
k.init()
print( k.account.id )