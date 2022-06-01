"""
	Get account owner full name
"""

from kard_private_api import Kard

app = Kard()
app.init()

print(app.account.firstname, app.account.lastname)