"""
	Block your cards
"""

from kard_private_api import Kard

app = Kard()
app.init()

# Block physical
card = app.cards.physicals[0]
app.cards.block_by_id( card['id'] )

# Block virtual
vcard = app.cards.virtuals[0]
app.cards.block_by_id( vcard['id'] )