"""
	Login to your Kard account
"""

from kard_private_api import Kard


app = Kard()
app.init()

print( app.login.is_still_logged_in )