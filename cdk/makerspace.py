
from aws_cdk import (
    Stage,
    Stack,
    Environment,
    aws_secretsmanager
)
from constructs import Construct

from visit import Visit
from api_gateway.shared_api_gateway import SharedApiGateway
from api_gateway.backend_api import BackendApi
from database import Database
from dns import (MakerspaceDnsRecords, MakerspaceDns, Domains)
from cognito.cognito_construct import CognitoConstruct
# from data_migration import DataMigrationStack

class MakerspaceStage(Stage):
    def __init__(self, scope: Construct, stage: str, *,
                 env: Environment) -> None:
        super().__init__(scope, stage, env=env)
        
        self.service = MakerspaceStack(self, stage, env=env)


class MakerspaceStack(Stack):

    def __init__(self, app: Construct, stage: str, *,
                 env: Environment):
        super().__init__(
            app,
            'MakerspaceStack',
            env=env,
            termination_protection=True)

        self.app = app
        self.stage = stage
        self.env = env

        self.domains = Domains(self.stage)

        self.create_dns = 'dev' not in self.domains.stage
        
        self.hosted_zones_stack()

        self.database_stack()

        # Get the api key value to use for backend api requests
        secret_name: str = "SharedApiGatewayKey"
        shared_gateway_secret = aws_secretsmanager.from_secret_name_v2(
                self.app,
                "SharedGatewaySecret",
                secret_name
        )
        backend_api_key: str = str(shared_gateway_secret.secret_from_json("backend_api_key"))

        self.visitors_stack(backend_api_key)

        self.backend_stack()

        if self.create_dns:
            self.dns_records_stack()

        self.shared_api_gateway(backend_api_key=backend_api_key)
        
        self.cognito_setup()
        
        # if self.stage.lower() == 'prod':
        #     self.data_migration_stack()
        
        # Set permissions for each lambda function to respective DDB table
        self.database.visits_table.grant_read_write_data(
            self.backend_api.lambda_visits_handler)

        self.database.users_table.grant_read_data(self.backend_api.lambda_visits_handler)
        self.database.users_table.grant_read_data(self.backend_api.lambda_equipment_handler)
        self.database.users_table.grant_read_write_data(self.backend_api.lambda_users_handler)
        
        #! Do not have a lambda register handler
        # self.database.users_table.grant_read_write_data(
        #     self.backend_api.lambda_register_handler)
        
        self.database.equipment_table.grant_read_write_data(self.backend_api.lambda_equipment_handler)
        
        self.database.qualifications_table.grant_read_write_data(self.backend_api.lambda_qualifications_handler)
            
    # def data_migration_stack(self):
        
    #     self.migration = DataMigrationStack(self.app, self.stage, env=self.env)
        
    #     self.add_dependency(self.migration)
        

    def database_stack(self):

        self.database = Database(self.app, self.stage, env=self.env)

        self.add_dependency(self.database)

    def visitors_stack(self, backend_api_key: str = ""):

        self.visit = Visit(
            self.app,
            self.stage,
            create_dns=self.create_dns,
            zones=self.dns,
            env=self.env,
            backend_api_key=backend_api_key
        )

        self.add_dependency(self.visit)

    def backend_stack(self):

        self.backend_api = BackendApi(
            self.app,
            self.stage,
            self.database.users_table.table_name,
            self.database.visits_table.table_name,
            self.database.equipment_table.table_name,
            self.database.qualifications_table.table_name,
            zones=self.dns,
            env=self.env
        )

        self.add_dependency(self.backend_api)

    def shared_api_gateway(self, backend_api_key: str = ""):

        self.api_gateway = SharedApiGateway(
            self.app,
            self.stage,
            self.backend_api.lambda_users_handler,
            self.backend_api.lambda_visits_handler,
            self.backend_api.lambda_qualifications_handler,
            self.backend_api.lambda_equipment_handler,
            api=self.dns.api,
            backend_api_key=backend_api_key,
            env=self.env, zones=self.dns, create_dns=self.create_dns
        )

        self.add_dependency(self.api_gateway)

    def hosted_zones_stack(self):

        self.dns = MakerspaceDns(self.app, self.stage, create_dns=self.create_dns, 
                                 env=self.env)

        self.add_dependency(self.dns)

    def dns_records_stack(self):

        # Can only have cross-stack references in the same environment
        # There is probably a way around this with custom resources, but
        # for now we'll just use unique dns records for beta.
        #
        # See the Domains class where we note that we could use NS records
        # to share sub-domain space.
        self.dns_records = MakerspaceDnsRecords(
            self.app,
            self.stage,
            env=self.env,
            zones=self.dns,
            api_gateway=self.dns.api,
            visit_distribution=self.visit.distribution
        )

        self.add_dependency(self.dns_records)

    def cognito_setup(self):

        self.cognito = CognitoConstruct(
            self,
            "MakerspaceCognito",
            user_pool_name="MakerspaceAuth"
        )
