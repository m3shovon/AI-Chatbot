from django.test import TestCase
from inventoryAPI import settings
import requests
# Create your tests here.

def sendSms(to_number, customMessage, user=None):
    if settings.SMS_ENABLED is False: return None # currently for development purpose
    message = customMessage

    if to_number.startswith('+88'):
        number = to_number[1:] # remove +88
    elif to_number.startswith('88'):
        number = to_number 
    elif to_number.startswith('0'):
        number = '88' + to_number
    else:
        return '111'

    print(number)
    if(number is not None and len(number) == 13 and number.startswith('88')):
        return '000'
    else:
        return '111'
    # if number is not None and len(number) == 13 and number.startswith('88') and message is not None:
    #     # api end point
    #     URL = settings.SMS_HOST_URL
    #     PARAMS = {
    #         "APIKey": settings.SMS_API_KEY,
    #         "senderid": settings.SMS_API_SENDER_ID,
    #         "channel": settings.SMS_CHANNEL,
    #         "DCS": settings.SMS_DCS,
    #         "flashsms": settings.SMS_FLASH,
    #         "number": number,
    #         "text": message
    #     }
    #     response = requests.get(url=URL, params=PARAMS)
    #     JsonResponse = response.json()
    #     print(JsonResponse)
    #     return JsonResponse['ErrorCode']
    # else:
    #     print("Invalid Phone or Message")

class SMSIntegrationTest(TestCase):
    def test_sms_integration(self):
        self.assertEqual(sendSms('+8801671080275', 'Testing Sms Integration without country code'), '000')
        self.assertEqual(sendSms('8801671080275', 'Testing Sms Integration without country code'), '000')
        self.assertEqual(sendSms('01671080275', 'Testing Sms Integration without country code'), '000')
        self.assertEqual(sendSms('+801671080275', 'Testing Sms Integration without country code'), '111')
        self.assertEqual(sendSms('801671080275', 'Testing Sms Integration without country code'), '111')
        self.assertEqual(sendSms('1671080275', 'Testing Sms Integration without country code'), '111')
