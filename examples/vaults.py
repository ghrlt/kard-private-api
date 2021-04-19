import api as A #Assuming `api.py` is in same directory
import random

A.login() #First time only

Acc = A.Account

vault = Acc.Vault('Example')

#Create our vault -- Not needed if the vault "Example" already exist
vault.create(goal=144)

#Fetch vault data
print( "Vault ID:", vault.id() )
print( "Vault Goal:", vault.goal() )
print( "Vault Balance:", vault.balance() )
print( "Vault Emoji:", vault.emoji() )
print( "Vault Color:", vault.color() )

#Modify vault
vault.changeColor("#00FF00")
print( "New vault Color:", vault.color() )

vault.changeEmote(emote=random.choice(["🎁", "🎈", "🛍", "💰", "😈", "🎓", "🏝", "🎫", "🎸", "✈️", "👟", "📱", "🎮", "🛴", "🛵"]))
print( "New vault Emoji:", vault.emoji() )

#Add money to the vault
vault.topup(amount=50)
print( "New vault Balance:", vault.balance() )

#Close the vault
vault.empty()
