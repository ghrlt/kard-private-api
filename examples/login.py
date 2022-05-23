"""
	Login to your Kard account
"""

from v2 import Kard


app = Kard()
app.init()

print( app.login.is_still_logged_in )