# A private API for Kard bank interaction

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

---

I did this by accident, I wanted to do a private api of my Wiz lamp but I haven't succeeded yet. and so, I wanted to look at my bank app..

I'm posting on Github today to show you how easy it is to control a Kard bank account, without much more security than that... 

## Usage
* [Login](#login)
* [Details](#account-details)
	* [Set details](#account-set-details)
* [Parent](#account-parent)
* [Friends](#account-friends)
* [Subscription](#account-subscription-plan)
* [Cards](#account-cards)



> Note: All the "[...]" are there only to hide my personal information. The informations returned by the API are not censored.

### Login

To login, you need to get a unique vendorID (identifier), generate a UUID and replace, or not, by ghrlt by android/ios (in config.json)
then, login: You can either put a phone number and your access code, or use these from config.json
```python
>>> login("06 12 34 56 78", "1234")
eyJhbGc[...]UIPrUxpZtI
```
First login with a identifier will require you to receive a SMS and confirm the OTP code. Python will ask it to you
Until you change your identifier, you will not need to login
	
Some function require your app code, you can either store it in config.json or precize it when you call the function



### Account details
```python
>>> Account.Firstname()
"Gaëtan"

>>> Account.Email()
"Gaetan@ghrlt.xyz"

>>> Account.Avatar()
"https://app.kard.eu/rails/active_storage/blobs/eyJfcm[...]c7665/cropped2039795875.jpg"
```
	
### Account set details
```python
>>> Account.setEmail("Bank@ghrlt.xyz")
200

>>> Account.setPhone("07 12 34 56 78", "1234")
200

>>> Account.setUsername('ghrlt-dev')
200
```

### Account Parent
```python
>>> Account.Parent.ID()
Z2lkOi8[...]TI5ZGNmMDc4YTU

>>> Account.Parent.Firstname()
"F[...]n"

>>> Account.Parent.Lastname()
"H[...]t"

>>> Account.Parent.Email()
"f[...]@gmail.com"

>>> Account.Parent.Phone()
"06 12 34 56 78"
```

### Account Friends
```python
>>> Account.Friends.howMany()
2

>>> Account.Friends.firstNames()
['A[...]n', 'F[...]n']
```

### Account Subscription plan
```python
>>> Account.Subscription.Status()
"ACTIVE"

>>> Account.Subscription.Name()
"Free Karder"

>>> Account.Subscription.Price()
0.0

>>> Account.Subscription.NextBillingDate()
None

>>> Account.Subscription.NextBillingPrice()
None
```

### Account Cards
```python
>>> Account.Cards.getAll()
[
  {
    '__typename': 'VirtualCard',
	'id': 'Z2lk[...]hM2I',
	'activatedAt': '1970-01-01T00:00:00Z', 
	'customText': None,
	'name': 'GAETAN HRLT',
	'visibleNumber': '5249 **** **** [...]',
	'blocked': False
  },
  {
    '__typename': 'PhysicalCard', 
	'id': 'Z2lk[...]3ZTg', 
	'activatedAt': '1970-01-01T00:00:00Z', 
	'customText': 'UNLIMITED MONEY', 
	'name': 'GAETAN HRLT', 
	'visibleNumber': '5249 **** **** [...]', 
	'blocked': False, 
	'atm': True, 
	'contactless': True, 
	'swipe': True,
	'online': True,
	'design': 'BLACK'
  }
]

>>> Account.Cards.PhysicalID()
"Z2lk[...]3ZTg"

>>> Account.Cards.VirtualID()
"Z2lk[...]hM2I"

>>> Account.Cards.getDetails(Account.Cards.VirtualID())
{'digits': '5249[...]', 'expiration': '1973-01-01', 'cvv': '123'}

>>> Account.Cards.getTopupCard()
{
  'id': 'Z2lk[...]mRmYw', 
  'name': 'Treezor Sas *1234', 
  'expiration': '01/01', 
  'last4Digits': '1234', 
  'isDefault': True, 
  'providSrcID': 'src_hkp[...]ta', 
  'providPayID': 'pay_r5h[...]nu'
}

>>> Account.Cards.defaultCardPaiementID()
"src_hk[...]ta"

>>> Account.Cards.block(Account.Cards.PhysicalID())
200	

>>> Account.Cards.unblock(Account.Cards.PhysicalID())
200

>>> Account.Cards.getVirtualCardNumber()
"5249[...]"

>>> Account.Cards.getVirtualCardExpiration()
"1973-01-01"

>>> Account.Cards.getVirtualCardCVV()
"123"

#IBAN
>>> Account.Cards.getBankID()
"Z2lk[...]kwOQ"

>>> Account.Cards.getIban()
"FR761437[...]36"

>>> Account.Cards.getBic()
"SFPMFRP1"
```

### Statistiques
```python
>>> Account.Stats.recentTransaction(2) #Default to 20
[
  {
    '__typename': 'CardTransaction', 
    'id': 'Z2lk[...]I2OA', 
    'title': 'Www.Aliexpress.Com', 
    'status': 'SETTLED', 
    'visibility': 'HIDDEN', 
    'amount': {'value': -15.38, 'currency': {'symbol': '€'}}, 
    'category': {'name': 'Shopping', 'color': '#F943B1', 'image': {'url': 'https://app.kard.eu/rails/active_storage/blobs/eyJfcmFp[...]2d498981/Shopping.png'}},
    'processedAt': '1970-01-01T00:00:01Z'
  },
  {
    '__typename': 'InternalTransferTransaction',
    'id': 'Z2lk[...]ZhMQ', 
    'title': 'Argent économisé', 
    'status': 'SETTLED', 
    'visibility': 'HIDDEN', 
    'amount': {'value': -10.0, 'currency': {'symbol': '€'}}, 
    'category': {'name': 'Internal transfer', 'color': '#6FFB9F', 'image': {'url': 'https://app.kard.eu/rails/active_storage/blobs/eyJfcmFp[...]24259d53/Ico-Top%20Up.png'}}, 
    'processedAt': '1970-01-01T00:00:00Z',
    'moneyAccount': {'name': 'Économies', 'color': '#64FF33', 'emoji': {'name': 'moneybag', 'unicode': '💰'}}
  }
]

>>> Account.Stats.totalTransactions()
92

>>> Account.Stats.week()
{
  'Shopping': {'amount': -15.38, 'percent': 100.0, 'nbTransa': 1},
  'total': 15.38
}

>>> Account.Stats.month()
{
  'Shopping': {'amount': -15.38, 'percent': 100.0, 'nbTransa': 1},
  'total': 15.38
}

>>> Account.Stats.year()
{
  'Shopping': {'amount': -156.93, 'percent': 73.47, 'nbTransa': 12},
  'Groceries': {'amount': -36.98, 'percent': 17.31, 'nbTransa': 2},
  'Entertainment': {'amount': -19.68, 'percent': 9.21, 'nbTransa': 4},
  'total': 213.59
}

>>> Account.Stats.all()
{
  'Shopping': {'amount': -500.13, 'percent': 82.12, 'nbTransa': 57},
  'Groceries': {'amount': -80.4, 'percent': 13.2, 'nbTransa': 7},
  'Entertainment': {'amount': -27.51, 'percent': 4.52, 'nbTransa': 6},
  'Bills': {'amount': -0.99, 'percent': 0.16, 'nbTransa': 1},
  'total': 609.03
}
```
### Money related
```python
>>> Account.Money.balance()
9.62

#You need to put, cvv amount and paiement card ID
>>> Account.Money.addFromSaved("123", "10", Account.Cards.defaultCardPaiementID())
"You now need to confirm 3D Secure code here: https://api2.checkout.com/v2/3ds/acs/sid_toiw6t7[...]m5rm"

>>> Account.Money.send()

```






## License

[GNU GPLv3](https://github.com/ghrlt/kard-private-api/blob/master/LICENSE)

## Disclaimer
I shall not, and will not be liable for any misuse or unauthorised use. 
This API is to be used for educational purposes only.


## Support me
<img alt="Support me through bank card" src="https://www.svgrepo.com/show/301678/piggybank-pig.svg" href="https://s.kard.eu/ghrlt/5.0" width="40" height="40"> <img alt="Send me a Discord Nitro" src="https://discord.com/assets/f8389ca1a741a115313bede9ac02e2c0.svg" href="https://discord.gg/cQY9hc7XHm" width="40" height="40"> <img alt="Subscribe to Kard" src="https://uploads-ssl.webflow.com/5fc53498e2555190106eb531/5fc5a6996e50deb8447505e4_logo-purple.svg" href="https://kard.eu?r=GAEHER" width="40" height="40">
