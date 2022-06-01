"""
	Get topup cards
"""

from kard_private_api import Kard

app = Kard()
app.init()

print( app.cards.used_for_topup )