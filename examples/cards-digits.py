"""
	Obtain your cards informations
"""

from kard_private_api import Kard

app = Kard()
app.init()

print( app.cards.physicals[0] )

vcards = app.cards.virtuals
if vcards:
	print( vcards[0] )

	print( app.cards.virtuals_digits[0] )