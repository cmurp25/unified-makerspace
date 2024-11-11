import json
import boto3
from boto3.dynamodb.conditions import Key
import os
import logging

# Not used
# import pdb
# import dateutil.tz
# import time

# For processing graduation date calculation
# from typing import Tuple

# For timestamp, if used
# from datetime import datetime
# from zoneinfo import ZoneInfo

class RegisterUserFunction():
    """
    This class wraps the function of the lambda so we can more easily test
    it with moto. In production, we will continue to pass the stood-up
    dynamodb table to the handler itself. However, when initializing this class,
    we can choose to instead initialize it with a mocked version of the
    dynamodb table.
    """

    def __init__(self, original_table, users_table, dynamodbclient):
        # Sets up CloudWatch logs and sets level to INFO
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        if dynamodbclient is None:
            self.dynamodbclient = boto3.client('dynamodb')
        else:
            self.dynamodbclient = dynamodbclient

        self.USERS_TABLE_NAME = os.environ["USERS_TABLE_NAME"]
        if users_table is None:
            dynamodbresource = boto3.resource('dynamodb')
            self.users = dynamodbresource.Table(self.USERS_TABLE_NAME)
        else:
            self.users = users_table

        self.ORIGINAL_TABLE_NAME = os.environ["ORIGINAL_TABLE_NAME"]
        if original_table is None:
            self.original = dynamodbresource.Table(
                self.ORIGINAL_TABLE_NAME)
        else:
            self.original = original_table
    
    def bad_request(body):
        HEADERS = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': os.environ["DOMAIN_NAME"],
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
        
        return {
            'headers': HEADERS,
            'statusCode': 400,
            'body': json.dumps(body)
        }

    def add_user_info(self, user_info):
        """
        Logs a user entry into the users table with the specified attributes.
        """
        
        self.logger.info('Starting add_user_info function')
        
        #? Do we want a timestamp variable? 
        # Generate timestamp in EST in the format YYYY-MM-DDTHH:mm:SS
        # timestamp = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%dT%H:%M:%S')
        
        try:
            user_id = user_info['user_id']
            
            #? Should we have college acronym collected too? 
            # dict for entry into the users table
            user_table_item = {
                'user_id':              {'S': user_id},
                'college':              {'S': user_info['college'] or ''},
                'major':                {'S': user_info['major'] or ''},
                'undergraduate_class':  {'S': user_info['undergraduate_class'] or ''},
                'university_status':    {'S': user_info['university_status'] or ''}
            }

            #! What are we doing for testing? 
            # if the json is from a test request it will have this ttl attribute
            # if "last_updated" in user_info:
            #     user_table_item['last_updated'] = {"N":str(user_info['last_updated'])}

            #! Insert items like this or like log_visit.py?
            user_table_response = self.dynamodbclient.put_item(
                TableName=self.USERS_TABLE_NAME,
                Item=user_table_item
            )  
            self.logger.info(f'User registration entry sucessfully added, response: {user_table_response}')

            return user_table_response['ResponseMetadata']['HTTPStatusCode']
        except Exception as e:
            self.logger.error(f'FAILED -- Error in add_user_info: {str(e)} \n\tCheck to see if user_id is passed in correctly.')
            raise

    def handle_register_user_request(self, request, context):
        self.logger.info('Handling register user request')
        
        HEADERS = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': os.environ["DOMAIN_NAME"],
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
        if (request is None):
            return {
                'headers': HEADERS,
                'statusCode': 400,
                'body': json.dumps({
                    "Message": "Failed to provide parameters"
                })
            }

        # Get all of the user information from the json file
        user_info = json.loads(request["body"])
        # Call Function
        response = self.add_user_info(user_info)
        # Send response
        return {
            'headers': HEADERS,
            'statusCode': response
        }


register_user_function = RegisterUserFunction(None, None, None)


def handler(request, context):
    # Register user information from the makerspace/register console
    # Since this will be hit in prod, it will go ahead and hit our prod
    # dynamodb table
    return register_user_function.handle_register_user_request(request, context)
