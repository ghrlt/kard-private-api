"""
	Get balance
"""

from v2 import Kard

app = Kard()
app.init()

print(f"{app.bank.balance}€")