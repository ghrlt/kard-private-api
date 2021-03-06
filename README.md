# A private API for Kard bank interaction


I did this by accident, I wanted to do a private api of my Wiz lamp but I haven't succeeded yet. and so, I wanted to look at my bank app..
I'm posting on Github today to show you how easy it is to control a Kard bank account, without much more security than that... 

## Usage

* [Details](#account-details)
	* [Set details](#account-set-details)
* [Parent](#account-parent)
* [Friends](#account-friends)
* [Subscription](#account-subscription-plan)
* [Cards](#account-cards)



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
['Antonin', 'Fabien']
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
Z2lk[...]3ZTg

>>> Account.Cards.VirtualID()
Z2lk[...]hM2I

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

>>> Account.Cards.block(Account.Cards.PhysicalID())
200	

>>> Account.Cards.unblock(Account.Cards.PhysicalID())
200

>>> Account.Cards.getVirtualCardNumber()
5249[...]

>>> Account.Cards.getVirtualCardExpiration()
1973-01-01

>>> Account.Cards.getVirtualCardCVV()
123

#IBAN
>>> Account.Cards.getBankID()
Z2lk[...]kwOQ

>>> Account.Cards.getIban()
FR761437[...]36

>>> Account.Cards.getBic()
SFPMFRP1
```


## License

[GNU GPLv3](https://github.com/ghrlt/kard-private-api/blob/master/LICENSE)

## Disclaimer
I shall not, and will not be liable for any misuse or unauthorised use. 
This API is to be used for educational purposes only.


## Support me
<img alt="Support me through bank card" src="https://www.svgrepo.com/show/301678/piggybank-pig.svg" href="https://s.kard.eu/ghrlt/5.0" width="40" height="40"> <img alt="Send me a Discord Nitro" src="https://discord.com/assets/f8389ca1a741a115313bede9ac02e2c0.svg" href="https://discord.gg/cQY9hc7XHm" width="40" height="40"> <img alt="Subscribe to Kard" src="https://uploads-ssl.webflow.com/5fc53498e2555190106eb531/5fc5a6996e50deb8447505e4_logo-purple.svg" href="https://kard.eu?r=GAEHER" width="40" height="40">
