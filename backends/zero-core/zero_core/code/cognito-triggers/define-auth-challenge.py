import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event):
    logger.info('Event: ', json.dump(event, None, 2))
    
    if (event.request.session & event.request.session.length & slice(event.request.session, -1)[0].challengeName == "SRP_A"):
        logger.info('New CUSTOM_CHALLENGE', json.dump(event, None, 2))
        
        event.request.session = []
        event.response.issueTokens = False
        event.response.failAuthentication = False
        event.response.challengeName = 'CUSTOM_CHALLENGE'
    
    elif (event.request.session &
        event.request.session.length &
        event.request.session.slice(-1)[0].challengeName == 'CUSTOM_CHALLENGE' &
        event.request.session.slice(-1)[0].challengeResult == True):
        
        
        logger.info('The user provided the right answer to the challenge; succeed auth')
        event.response.issueTokens = True
        event.response.failAuthentication = False
        
    elif (event.request.session & event.request.session.length >= 4 & slice(event.request.session, -1)[0].challengeResult == False):
        logger.info('FAILED Authentication: The user provided a wrong answer 3 times')
        event.response.issueTokens = False
        event.response.failAuthentication = True
        
    else:
        logger.info('User response incorrect: Attempt [' + event.request.session.length + ']');
        event.response.issueTokens = False
        event.response.failAuthentication = False
        event.response.challengeName = 'CUSTOM_CHALLENGE'
        
    logger.info('Output: ', json.dump(event, None, 2))
    return event