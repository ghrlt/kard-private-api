"""
	Get full IBAN / RIB
"""

from kard_private_api import Kard

app = Kard()
app.init()

print( app.bank.iban )