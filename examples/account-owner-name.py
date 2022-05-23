"""
	Get account owner full name
"""

from v2 import Kard

app = Kard()
app.init()

print(app.account.firstname, app.account.lastname)