"""
	Cashback related things	
"""

from v2 import Kard

app = Kard()
app.init()


is_active = app.cashback.is_cashback_active
if is_active:
	print("Cashback is enabled on your account")
	print(f"You currently earned {app.cashback.total_earned}€ and still have {app.cashback.pending_cashout}€ to cashout")

	if input("Wanna see current available cashback offers? (yes/no)").lower() == "yes":
		offers = app.cashback.current_offers

		for offer in offers:
			print(offer['name'], "-", f"{offer['rate']}%")
			print(offer['description'])
			print()
			print(offer['legalTerms'])
			#... there's more data displayable

else:
	print("Cashback is not enabled on your account..")