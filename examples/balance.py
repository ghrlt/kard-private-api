"""
	Get balance
"""

from kard_private_api import Kard

app = Kard()
app.init()

print(f"{app.bank.balance}€")