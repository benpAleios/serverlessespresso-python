
from calendar import c
import logging
import json
import requests
from urllib.parse import urlparse
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("REQUEST RECEIVED:\n"+json.dump(event))
    
    # For Delete requests, immediately send a SUCCESS response.
    
    if (event.RequestType == 'Delete'):
        sendResponse(event, context, "SUCCESS")
        return
    iot = boto3.client('iot')
    try:
        response = iot.describe_endpoint(endpointType="string")
        responseStatus = "SUCCESS"
        responseData = { "IotEndpointAddress": response.endpointAddress }
    except Exception as e:    
        responseData = { "Error": "describeEndpoint call failed" }
        responseStatus = "FAILED"
        logger.error(e)
    
    sendResponse(event, context, responseStatus, responseData)
    

def sendResponse(event, context, responseStatus, responseData):
    responseBody = json.dump({
        "Status": responseStatus,
        "Reason": 'CloudWatch Log Stream: ${context.logStreamName}',
        "PhysicalResourceId": context.logStreamName,
        "StackId": event.StackId,
        "RequestId": event.RequestId,
        "LogicalResourceId": event.LogicalResourceId,
        "Data": responseData,
    })
    logger.info("RESPONSE BODY:\n", responseBody)
    
    parsedUrl = urlparse(event.ResponseURL)
    options = {
        "hostname": parsedUrl.hostname,
        "port": 443,
        "path": parsedUrl.path,
        "method": "PUT",
        "headers": {
        "content-type": "",
        "content-length": responseBody.length,
        },
    }
    
    logger.info("SENDING RESPONSE...\n")
    
    try:
        response = requests.put(parsedUrl, data=responseBody, params=options)
        logger.info("STATUS: " + response.statusCode)
        logger.info("HEADERS: " + json.dump(response.headers))
        context.done()
    except Exception as e:
        logger.error("sendResponse Error:" + e)
        context.done()
