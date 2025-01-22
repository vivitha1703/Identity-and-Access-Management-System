import os
from twilio.rest import Client
import phonenumbers

account_sid = 'ACcca6975e72346c3683bcabf2b2776615'
auth_token = '00473e83ad9ca1a6f4fe035c86da05c1'
client = Client(account_sid, auth_token)

import phonenumbers

def validate_and_format_phone(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        else:
            print("Invalid phone number.")
            return None
    except phonenumbers.NumberParseException:
        print("Error parsing phone number.")
        return None

def send_sms(user_code, phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "IN") 
        print(f"Formatted phone number: {parsed_number}")
        valid_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164) 
        message = client.messages.create(
            body=f'Hi! Your user and verification code is {user_code}',
            from_='+17208361002',
            to=valid_number
        )
        print(f"Message sent: {message.sid}") 
    except phonenumbers.phonenumberutil.NumberParseException as e:
        print(f"Error parsing phone number: {e}")
