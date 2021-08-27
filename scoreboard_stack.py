from aws_cdk import (core,
                     aws_apigateway as apigw,
                     aws_s3 as s3,
                     aws_lambda as lambda_,
                     aws_lambda_python as lambda_python
                     )





class ScooreboardStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
        # lambda_layer = lambda_python.PythonLayerVersion(
        #        self, 'CloudscraperLayer',
        #    #    entry='.venv/lib/python3.9/site-packages/cloudscraper',
        #        entry='/Users/kujapek/projects/python/game-stats/.venv/lib/python3.9/site-packages/cloudscraper',
        #        compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        #        description='Cloudscraper Library',
        #        layer_version_name='v1'
        #    )

        score_lambda = lambda_python.PythonFunction(
            self,
            'scoreboard-function',
            entry='resources',
            index='game_processor.py',
            runtime=lambda_.Runtime.PYTHON_3_8,
            timeout=core.Duration.seconds(20),
        #    layers=[lambda_layer],
            handler='lambda_handler')        
        
        #Create an API GW Rest API
        base_api = apigw.RestApi(self, 'ApiGW',rest_api_name='ScoreboardAPI')

        #Create a resource on the base API
        api_resource = base_api.root.add_resource('scoreboard', default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS))

        lambda_integration = apigw.LambdaIntegration(
            score_lambda,
            proxy=False,
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Content-Type': "'text/html; charset=utf-8'"
                },
                'responseTemplates': {
                    'text/html': "$input.path('body')"
                }
            }]
        )

        api_resource.add_method('GET', lambda_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                    'method.response.header.Content-Type': True
                }
            }])
