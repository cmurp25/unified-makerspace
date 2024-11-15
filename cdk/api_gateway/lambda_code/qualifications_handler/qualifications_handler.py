import json
from pydoc import cli
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from ..api_defaults import *

class LogQualificationFunction():
    def __init__(self, qualifications_table):
        # TODO: Setup CloudWatch Logs
        # Sets up CloudWatch logs and sets level to INFO
        # self.logger = logging.getLogger()
        # self.logger.setLevel(logging.INFO)
        
        if qualifications_table is None:
            # Get the service resource.
            dynamodb = boto3.resource('dynamodb')
            # Get the table name.
            QUALIFICATIONS_TABLE_NAME = os.environ["QUALIFICATIONS_TABLE_NAME"]
            # Get table objects
            self.qualifications_table = dynamodb.Table(QUALIFICATIONS_TABLE_NAME)
        else:
            self.qualifications_table = qualifications_table
            
    # Main handler function
    def qualifications_handler(self, event, context):
        """ 
        Handles the request of what the user is trying accomplish with any endpoint regarding qualifications.
        Based on the request, it will route to the appropriate function to accomplish the request.
        Performs validation checks and creates return responses based on success/fail.
        """
        try:
            method_requires_body: list = ["POST", "PATCH"]

            response = buildResponse(statusCode = 400, body = {})
            http_method: str = event.get("httpMethod")
            resource_path: str = event.get("resource")

            # Get a user_id if needed
            user_id: str = ""
            if user_endpoint in resource_path:
                user_id = event['pathParameters'].get('user_id')

                # Make sure no '@' is in user_id
                if len(user_id.split("@")) > 1:
                    errorMsg: str = "user_id can't be an email."
                    body = { 'errorMsg': errorMsg }
                    return buildResponse(statusCode = 400, body = body)

            # Get the body data if needed
            data:dict = {}
            if http_method in method_requires_body:
                if 'body' not in event:
                    errorMsg: str = "REST method {http_method} requires a request body."
                    body = { 'errorMsg': errorMsg }
                    return buildResponse(statusCode = 400, body = body)
                data = json.loads(event['body'])

            # Try to get any query parameters
            try:
                query_parameters: dict = event['queryStringParameters']

                # Remove unknown query parameters
                for key in query_parameters:
                    if key not in VALID_QUERY_PARAMETERS:
                        del query_parameters[key]
                    if key in INT_QUERY_PARAMETERS:
                        query_parameters[key] = int(query_parameters[key])
            except:
                query_parameters: dict = {}

            # Qualifications information request handling
            if http_method == "GET" and resource_path == qualifications_path:
                response = self.get_all_qualifications_information(query_parameters)
            elif http_method == "POST" and resource_path == qualifications_path:
                response = self.create_user_qualifications(data)

            elif http_method == "GET" and resource_path == qualifications_param_path:
                response = self.get_user_qualifications(user_id)
            elif http_method == "PATCH" and resource_path == qualifications_param_path:
                response = self.patch_user_qualifications(user_id, data)


            return response
        except:
            errorMsg: str = f"We're sorry, but something happened. Try again later."
            body = { 'errorMsg': errorMsg }
            return buildResponse(statusCode = 500, body = body)
            
    ################################################
    # Qualifications information function handlers #
    ################################################
    def get_all_qualifications_information(self, query_parameters: dict):
        """
        Returns all the qualifications information entries from the qualifications table.

        :params query_parameters: A dictionary of parameter names and values to filter by.
        """
        
        if query_parameters:
            try:
                timestamp_expression = buildTimestampKeyExpression(query_parameters, 'last_updated')

            except InvalidQueryParameters as iqp:
                body = { 'errorMsg': str(iqp) }
                return buildResponse(statusCode = 400, body = body)

            # Query for matching qualifcation entries
            try:
                key_expression = Key('_ignore').eq("1") & timestamp_expression
                items = queryByKeyExpression(self.qualifications_table, key_expression, GSI = TIMESTAMP_INDEX)

            except Exception as e:
                body = { 'errorMsg': "Something went wrong on the server." }
                return buildResponse(statusCode = 500, body = body)

            # Do a second lookup for all returned items to get the rest of the data
            qualifications = []
            for item in items:
                user_id = item['user_id']

                response = self.qualifications_table.get_item(
                    Key={ 'user_id': user_id }
                )

                qualifications.append(response['Item'])

        else:
            qualifications = scanTable(self.qualifications_table)

        body = { 'qualifications': qualifications }

        return buildResponse(statusCode = 200, body = body)

    def create_user_qualifications(self, data: dict):
        """
        Adds a qualifications information entry for a specified user to the qualifications table.

        :params user_id: The name of the user.
        :params data: The qualifications information entry to add.
        """
        
        try:
            self.validateQualificationRequestBody(data)
        except InvalidRequestBody as irb:
            body = { 'errorMsg': str(irb) }
            return buildResponse(statusCode = 400, body = body)

        # Check to make sure the user doesn't already exist. Return 400 if user does exist.
        user_id: str = data['user_id']
        response = self.get_user_qualifications(user_id)
        if response['statusCode'] == 200:
            errorMsg: str = f"User {user_id} qualifications already exist. Did you mean to update?"
            body = { 'errorMsg': errorMsg }
            return buildResponse(statusCode = 400, body = body)

        # Store the formatted current time in data['last_updated']
        data['last_updated'] = datetime.now(ZoneInfo("America/New_York")).strftime(TIMESTAMP_FORMAT)

        # If 'trainings' not in data, store an empty list
        if 'trainings' not in data:
            data['trainings'] = []

        # If 'waivers' not in data, store an empty list
        if 'waivers' not in data:
            data['waivers'] = []
        # Always force "_ignore" key to have value of "1"
        data['_ignore'] = "1"

        # Actually try putting the item into the table
        try:
            self.qualifications_table.put_item(
                Item=data
            )
        except Exception as e:
            body = { 'errorMsg': "Something went wrong on the server." }
            return buildResponse(statusCode = 500, body = body)

        # If here, put action succeeded. Return 201
        return buildResponse(statusCode = 201, body = {})

    def get_user_qualifications(self, user_id: str):
        """
        Gets the qualifications information entry for a specified user from the qualifications table.

        :params user_id: The name of the user.
        """

        """
        Query the table (because get_item doesn't play nice without specifying sort key).
        Limit the results to 1 since we are enforcing 1 qualifications entry per user.
        If an item already exists, this will return an "array" of 1 item in the 'Items'
        key. For these purposes, ['Items'][0] is equivalent to retrieving the desired
        user's qualifications.
        """
        response = self.qualifications_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                Limit=1
        )

        # User qualifications doesn't exist if length of response['Items'] == 0
        if len(response['Items']) == 0:
            errorMsg: str = f"No qualificationsfor the user {user_id} could be found. Is there a typo?"
            body = { 'errorMsg': errorMsg }
            return buildResponse(statusCode = 400, body = body)

        qualifications = response['Items'][0]

        return buildResponse(statusCode = 200, body = qualifications)

    def patch_user_qualifications(self, user_id: str, data: dict):
        """
        Updates the qualifications information entry for a specified user. Fails if the a
        qualifications entry does not exist for the user.

        :params user_id: The name of the user.
        :params data: The updated qualifications information entry.
        """

        # Ensure an entry to update actually exists
        response = self.get_user_qualifications(user_id)
        if response['statusCode'] != 200:
            errorMsg: str = f"User {user_id} could not be found. Did you mean to add the user?"
            body = { 'errorMsg': errorMsg }
            return buildResponse(statusCode = 400, body = body)

        else:
            # Load the json object stored in response['body']
            qualifications = json.loads(response['body'])

            """
            Because the last_updated timestamp will be changed (making a new copy),
            save a copy of the original entry to delete.
            """
            entry_to_delete = qualifications.copy()

        # "user_id" field is never allowed for update
        if 'user_id' in data:
            errorMsg: str = "Updating the 'user_id' field is not allowed. Please remove it before trying to update user {user_id}'s information."
            body = { 'errorMsg': errorMsg }
            return buildResponse(statusCode = 400, body = body)

        # Update data['last_updated'] and ensure data['_ignore'] == '1'
        data['last_updated'] = datetime.now(ZoneInfo("America/New_York")).strftime(TIMESTAMP_FORMAT)
        data['_ignore'] = '1'

        # Copy all all fields from data to user
        for key in data:
            qualifications[key] = data[key]

        # Validate new item
        try:
            qualifications = self.validateQualificationRequestBody(qualifications)
        except InvalidRequestBody as irb:
            body = { 'errorMsg': str(irb) }
            return buildResponse(statusCode = 400, body = body)
        
        # Try putting item back into table
        self.qualifications_table.put_item(Item=qualifications)

        # Delete the old entry
        self.qualifications_table.delete_item(
            Key={
                'user_id': entry_to_delete['user_id'],
                'last_updated': entry_to_delete['last_updated']
            }
        )

        # Successfully updated user
        return buildResponse(statusCode = 204, body = {})
    
    def validateQualificationRequestBody(self, data: dict):
        """
        Valides the request body used when adding/updating user information.
        Removes any unnecessary keys and values from the request body.
        Will raise an InvalidRequestBody error with the details explaining
        what part of the body is invalid.

        :params user_id: The name of the user.
        :params data: The request body to validate.
        :returns: A valid qualifications request body.
        :raises: InvalidRequestBody
        """

        required_fields: list[str] = ["user_id", "trainings", "waivers"]
        completable_item_lists: list[str] = ["trainings", "waivers"]
        completable_item_fields: list [str] = ["name", "completion_status"]
        valid_completion_statuses: list[str] = ["Complete", "Incomplete"]

        # Ensure all required fields are present
        if not allKeysPresent(required_fields, data):
            errorMsg: str = f"Missing at least one field from {required_fields} in request body. 'trainings' and 'waivers' can be empty lists."
            raise InvalidRequestBody(errorMsg)

        for completable_list in completable_item_lists:
            for item in data[completable_list]:
                if not allKeysPresent(completable_item_fields, item):
                    errorMsg: str = f"Missing at least one field from {completable_item_fields} for at least one completeable item in {completable_list}."
                    raise InvalidRequestBody(errorMsg)

                name = str(item['name'])
                status = str(item['completion_status'])
                if status not in valid_completion_statuses:
                    errorMsg: str = f"Completion status '{status}' is not one of the valid completion statuses {valid_completion_statuses} for object with name {name} in {completable_list}."
                    raise InvalidRequestBody(errorMsg)

        return data

            
log_qualification_function = LogQualificationFunction(None)

def handler(request, context):
    return log_qualification_function.qualifications_handler(request, context)