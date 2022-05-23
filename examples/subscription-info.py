"""
	Check your subscription plan
"""

from v2 import Kard

app = Kard()
app.init()


if app.subscription.is_free_karder:
	print( "You are a legacy Karder!", "That means that your account is free of fees" )
else:
	if app.subscription.is_active:
		print("You have an active subscription.")
		print(f"You're paying {app.subscription.price}")
		print(f"Next billing is planned on {app.subscription.next_billing['date']}")