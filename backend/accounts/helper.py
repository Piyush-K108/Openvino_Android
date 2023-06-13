from django.conf import settings
import random
from twilio.rest import Client


class MessageHandler:
    phone  = None
    otp = None
    def __init__(self,phone,otp) -> None:
        self.phone = phone
        self.otp = otp
    def set_otp(self):
        client = Client(settings.SID,settings.TOKEN)

        message = client.messages.create(
                                        body=f'Your otp is :{self.otp}',  
                                        from_ = '+14302434103',
                                        to =self.phone          
                                            )
        return message
