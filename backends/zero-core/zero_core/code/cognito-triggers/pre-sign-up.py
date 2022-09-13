import json

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event):
    logger.info("Event: ", json.dump(event, None, 2))

    event.response.autoConfirmUser = True
    event.response.autoVerifyPhone = True
    return event
