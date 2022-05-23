"""
	Unblock your cards
"""

from v2 import Kard

app = Kard()
app.init()

# Block physical
card = app.cards.physicals[0]
app.cards.unblock_by_id( card['id'] )

# Block virtual
vcard = app.cards.virtuals[0]
app.cards.unblock_by_id( vcard['id'] )