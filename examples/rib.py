"""
	Get full IBAN / RIB
"""

from v2 import Kard

app = Kard()
app.init()

print( app.bank.iban )