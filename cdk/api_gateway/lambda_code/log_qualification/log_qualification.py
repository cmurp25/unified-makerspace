import json
from pydoc import cli
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

# Not used
# import re

class LogQualificationFunction():
    def __init__(self, qualifications_table, users_table):
        # Sets up CloudWatch logs and sets level to INFO
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        if qualifications_table is None:
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb')
            # Get the table name.
            QUALIFICATIONS_TABLE_NAME = os.environ["QUALIFICATIONS_TABLE_NAME"]
            # Get table objects
            self.qualifications = dynamodb.Table(QUALIFICATIONS_TABLE_NAME)
        else:
            self.qualifications = qualifications_table

        if users_table is None:
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb')
            # Get the table name.
            USERS_TABLE_NAME = os.environ["USERS_TABLE_NAME"]
            # Get table objects
            self.users = dynamodb.Table(USERS_TABLE_NAME)
        else:
            self.users = users_table
            
    def addQualificationEntry(self, user_info):
        """
        Logs a qualifications entry into the qualifications table
        with the specified attributes.
        """
        self.logger.info('Starting addQualificationEntry function')
        # Use if needed
        # self.logger.info(f'Received user_info: {user_info}')

        try:
            # Generate timestamp in EST in the format YYYY-MM-DDTHH:mm:SS
            last_updated = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%dT%H:%M:%S')
            self.logger.info(f'Generated timestamp (var: last_updated): {last_updated}')
            
            # Construct the item to be added to the qualifications table
            qualification_item = {
                'user_id': {'S': user_info['user_id']},
                'last_updated': {'S': last_updated},
                'trainings': {'L': user_info.get('trainings', [])},  # Defaults to empty list if not provided
                'waivers': {'L': user_info.get('waivers', [])},      # Defaults to empty list if not provided
                '_ignore': {'S': '1'}
            }

            # Record the qualification in the qualifications table
            qualifications_response = self.qualifications.put_item(
                Item=qualification_item
            )
            self.logger.info(f'Qualification entry added successfully, response: {qualifications_response}')

            # Return the HTTP status code of the response
            return qualifications_response['ResponseMetadata']['HTTPStatusCode']
        except Exception as e:
            self.logger.error(f'FAILED -- Error in addQualificationEntry: {str(e)}')
            raise
            
    def handle_log_qualification_req(self, request, context):
        """ 
        Log the qualifcations of a user.
        This should:
        1. Place qualifications entry into the qualifications table
        """
        
        self.logger.info('Handling log qualification request')
        
        HEADERS = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': os.environ["DOMAIN_NAME"],
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }

        def bad_request(body):
            return {
                'headers': HEADERS,
                'statusCode': 400,
                'body': json.dumps(body)
            }

        # if no request is provided (should never be the case because of gateway invocation)
        if (request is None):
            return bad_request({'Message': 'No request provided'})
        
        # get the body of the request
        body = json.loads(request.get('body', "{}"))

        # get the users user_id
        try:
            user_id = body['user_id']
        except KeyError:
            return bad_request({'Message': f'Missing parameter: user_id \n\tKeyError: {KeyError}'})
            
        status_code = self.addQualificationEntry(body)
        
        # Send response
        return {
            'headers': HEADERS,
            'statusCode': status_code
        }
            
log_qualification_function = LogQualificationFunction(None, None)

def handler(request, context):
    return log_qualification_function.handle_log_qualification_req(request, context)