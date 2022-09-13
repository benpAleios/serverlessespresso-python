from ast import Or
import logging
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event):
    logger.info("Event: ", json.dump(event, None, 2))
    
    expectedAnswer = event.request.privateChallengeParameters.passCode | None
    if (event.request.challengeAnswer == expectedAnswer):
        event.response.answerCorrect = True
    else:
        event.response.answerCorrect = False
    
    logger.info("Output: ", json.dump(event, None, 2))

    return event