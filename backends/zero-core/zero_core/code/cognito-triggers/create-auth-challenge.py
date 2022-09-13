import boto3
import logging
import random
import json

sns = boto3.client("sns")

TEXT_MSG = "[Serverlesspresso] Your registration code is: "
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event = {}):
    logger.info(event, None, 2)
    passCode = 0
    
    phoneNumber = event.request.userAttributes.phone_number
    if ((event.request.session &
         event.request.session.length &
         slice(event.request.session, -1)[0].challengeName == "SRP_A") |
        event.request.session.length == 0
        ):
        passCode = int(''.join(str(random.SystemRandom().randrange(3)) for i in range(6)))
        
        sendSMSviaSNS(phoneNumber, passCode)
        
    else:
        previousChallenge = slice(event.request.session, -1)[0] #this is wrong i think
        passCode = previousChallenge.challengeMetadata.match('/CODE-(\d*)/')[1] # so is this
        
        
    event.response.publicChallengeParameters = {
        "phone": event.request.userAttributes.phone_number,
    }
    event.response.privateChallengeParameters = { passCode }
    event.response.challengeMetadata = 'CODE-${passCode}'

    logger.info("Output: ", json.dump(event, None, 2))
    return event

    

# Send one-time password via SMS
async def sendSMSviaSNS(phoneNumber, passCode):
    params = {
        "Message": '${TEXT_MSG} ${passCode}',
        "PhoneNumber": phoneNumber,
    }
    result = await sns.publish(params)
    logger.info("SNS result: ", result)
    
