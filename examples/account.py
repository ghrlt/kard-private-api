import api as A #Assuming `api.py` is in same directory
import random

A.login() #First time only

Acc = A.Account
print("Account informations")
print( "Account id:", Acc.id() )
print( "Account type:", Acc.type() )
print( "Account creation date:", Acc.creationDate() )
print( "Account avatar:", Acc.avatar() )
print( "Account username:", Acc.username() )
print( "Account referral code:", Acc.referralCode() )
print( "Account referral link:", Acc.referralLink() )
print( "Account Slash link:", Acc.slashLink() ) #You can provide an amount parameter



print("\nAccount owner informations")
print( "Account owner firstname:", Acc.firstname() )
print( "Account owner lastname:", Acc.lastname() )
print( "Account owner age:", Acc.age() )
print( "Account owner birthdate:", Acc.birthDate() )
print( "Account owner birthplace:", Acc.birthPlace() )
print( "Account owner address:", Acc.address() )
print( "Account owner email:", Acc.email() )
print( "Account owner email confirmed status:", Acc.isEmailConfirmed() )
print( "Account owner phone:", Acc.phone() )

print("\nChange informations")
Acc.setUsername("Karder")
print( "New account username:", Acc.username() )

Acc.setEmail("karder@kard.com") #Don't forget to confirm in your mailbox
print( "New account owner email:", Acc.email() )

Acc.setPhone("+33 06 12 34 56 78") #You can provide a code parameter if it's not set in config.json 
print( "New account owner phone:", Acc.phone() )
