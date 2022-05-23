"""
	Get topup cards
"""

from v2 import Kard

app = Kard()
app.init()

print( app.cards.used_for_topup )