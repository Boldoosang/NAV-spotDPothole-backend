#Justin Baldeosingh
#SpotDPothole-Backend
#NULLIFY

#Import Modules
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask import current_app as app

#Generates a confirmation token for a given email, and returns the token.
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

#Returns an email address associated with a particular token.
def confirm_token(token, expiration=600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    #Attempts to get the email for a given token. 
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
    #Otherwise return false.
        return False

    #Returns the email associated with the token.
    return email
