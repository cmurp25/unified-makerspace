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

# Import log_visit for user registration checking
# and registrationWorkflow function
from ..log_visit import log_visit as LV

class LogEquipmentFunction():
    def __init__(self, equipment_table, users_table):
        # Sets up CloudWatch logs and sets level to INFO
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        if equipment_table is None:
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb')
            # Get the table name.
            EQUIPMENT_TABLE_NAME = os.environ["EQUIPMENT_TABLE_NAME"]
            # Get table objects
            self.equipment = dynamodb.Table(EQUIPMENT_TABLE_NAME)
        else:
            self.equipment = equipment_table

        if users_table is None:
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb')
            # Get the table name.
            USERS_TABLE_NAME = os.environ["USERS_TABLE_NAME"]
            # Get table objects
            self.users = dynamodb.Table(USERS_TABLE_NAME)
        else:
            self.users = users_table
            
    def addEquipmentEntry(self, user_info):
        """
        Logs a equipment entry into the equipment table
        with the specified attributes.
        """
        
        self.logger.info("Starting addEquipmentEntry function")
        # self.logger.info(f"Received user_info: {user_info}")
        
        try:
            # Generate timestamp in EST in the format YYYY-MM-DDTHH:mm:SS
            timestamp = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%dT%H:%M:%S')
            self.logger.info(f'Generated timestamp: {timestamp}')
            
            """
            #! Note: 
            Do we want to add some logic here to determine which variables we 
            want to store?
            
            Do we want to keep _ignore as '1'? 
            """
            # Construct the item to be added to teh visits table
            equipment_item = {
                'user_id': {'S': user_info['user_id']},
                'timestamp': {'S': timestamp},
                '3d_printer_info': {
                    'M': {
                        'printer_name': {'S': user_info.get('printer_name', '')},
                        'print_duration': {'S': user_info.get('print_duration', '')},
                        'print_mass': {'S': user_info.get('print_mass', '')},
                        'print_mass_estimate': {'S': user_info.get('print_mass_estimate', '')},
                        'print_notes': {'S': user_info.get('print_notes', '')},
                        'print_status': {'S': user_info.get('print_status', '')}
                    }
                },
                'advisor_name': {'S': user_info.get('advisor_name', '')},
                'class_number': {'S': user_info.get('class_number', '')},
                'department_name': {'S': user_info.get('department_name', '')},
                'difficulties_notes': {'S': user_info.get('difficulties_notes', '')},
                'equipment_type': {'S': user_info.get('equipment_type', '')},
                'faculty_name': {'S': user_info.get('faculty_name', '')},
                'intern_name': {'S': user_info.get('intern_name', '')},
                'issue_notes': {'S': user_info.get('issue_notes', '')},
                'location': {'S': user_info.get('location', '')},
                'more_colors': {'S': user_info.get('more_colors', '')},
                'organization_affiliation': {'S': user_info.get('organization_affiliation', '')},
                'present_makerday': {'S': user_info.get('present_makerday', '')},
                'print_name': {'S': user_info.get('print_name', '')},
                'project_name': {'S': user_info.get('project_name', '')},
                'project_sponsor': {'S': user_info.get('project_sponsor', '')},
                'project_type': {'S': user_info.get('project_type', '')},
                'recieved_filament_color': {'S': user_info.get('recieved_filament_color', '')},
                'referral_source': {'S': user_info.get('referral_source', '')},
                'requested_colors': {'S': user_info.get('requested_colors', '')},
                'resin_type': {'S': user_info.get('resin_type', '')},
                'satisfaction_rate': {'S': user_info.get('satisfaction_rate', '')},
                '_ignore': {'S': '1'}
            }
            
            equipment_response = self.equipment.put_item(
                Item=equipment_item
            )
            
            self.logger.info(f'Equipment entry added successfully, response: {equipment_response}')
            
            # Return the HTTP status code of the response
            return equipment_response['ResponseMetadata']['HTTPStatusCode']
        except Exception as e:
            self.logger.error(f'FAILED -- Error in addEquipmentEntry: {str(e)}')
            raise
            
    def handle_log_equipment_request(self, request, context):
        """
        Log the equipment use log of a user.
        This should:
        1. Verify user is registered?
        2. Place equipment log entry into the table
        """
        
        self.logger.info('Handling log equipment request')

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

        # send user the registration link if not registered
        user_registered = LV.isUserRegistered(user_id)
        if not user_registered:
            LV.registrationWorkflow(user_id)
        
        # add the visit entry
        status_code = self.addEquipmentEntry(body)

        # Send response
        return {
            'headers': HEADERS,
            'statusCode': status_code,
            'body': json.dumps({
                "was_user_registered": user_registered,
        })
    }
            
log_equipment_function = LogEquipmentFunction(None, None)

def handler(request, context):
    return log_equipment_function.handle_log_equipment_request(request, context)