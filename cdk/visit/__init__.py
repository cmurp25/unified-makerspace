
# from distutils.command.build import build
from aws_cdk import (
    Stack,
    Environment,
    aws_certificatemanager,
    aws_s3_deployment,
    aws_cloudfront,
    aws_cloudfront_origins,
    aws_s3,
    aws_iam,
    Duration,
    Aws
)
from constructs import Construct
from dns import MakerspaceDns
import logging

class Visit(Stack):
    """
    Track visitors to the makerspace via a simple web console. This
    exists as a backup in case the hardware scanner is not functional.

    This stack contains one primary part and the following workflow:

    1. A static web page asks for a Clemson username (visit.cumaker.space)
    2. An api call to the backend api is made to log the visit.
    3. The visits handler will consider any additional registration logic.
    4. The user has successfully logged a visit.
    """

    def __init__(self, scope: Construct,
                 stage: str,
                 *,
                 env: Environment,
                 create_dns: bool,
                 zones: MakerspaceDns = None,
                 backend_api_key: str = ""):

        super().__init__(scope, 'Visitors', env=env)
        
        # Sets up CloudWatch logs and sets level to INFO
        # self.logger = logging.getLogger()
        # self.logger.setLevel(logging.INFO)

        self.stage = stage
        self.create_dns = create_dns
        self.zones = zones

        self.source_bucket()

        self.cloudfront_distribution()


    def source_bucket(self):
        self.oai = aws_cloudfront.OriginAccessIdentity(
            self, 'VisitorsOriginAccessIdentity')
 
        self.bucket = aws_s3.Bucket(self, 'cumakerspace-visitors-console')
        self.bucket.grant_read(self.oai)

        # Deploy static files to the bucket
        aws_s3_deployment.BucketDeployment(
            self,
            'VisitorsConsoleDeployment',
            sources=[
                aws_s3_deployment.Source.asset(f'visit/console/{self.stage}/')
            ],
            destination_bucket=self.bucket
        )
        
    def cloudfront_distribution(self):

        kwargs = {}

        if self.create_dns:
            domain_name = self.zones.visit.zone_name
            kwargs['domain_names'] = [domain_name]
            kwargs['certificate'] = aws_certificatemanager.Certificate(
                self,
                'VisitorsCertificate',
                domain_name=domain_name,
                validation=aws_certificatemanager.CertificateValidation.from_dns(self.zones.visit)
            )

        # Configure default behavior
        kwargs['default_behavior'] = aws_cloudfront.BehaviorOptions(
            origin=aws_cloudfront_origins.S3Origin(
                self.bucket,
                origin_access_identity=self.oai
            ),
            viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
        )

        kwargs['default_root_object'] = "index.html"
        kwargs['price_class'] = aws_cloudfront.PriceClass.PRICE_CLASS_100

        # This error response redirect back to index.html because React handles everything in a page
        # including routing. when you add /register after the domain, there would be such key avaliable
        # in the static site. We need cloudfront redirect it back to index.html for React to
        # handle the routing.
        kwargs['error_responses'] = [
            aws_cloudfront.ErrorResponse(
                http_status=404,
                response_http_status=200,
                response_page_path="/index.html",
                ttl=Duration.seconds(10)
            )
        ]

        # Create CloudFront Distribution
        self.distribution = aws_cloudfront.Distribution(
            self, 'VisitorsConsoleCache', **kwargs
        )
