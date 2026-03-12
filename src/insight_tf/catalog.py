"""
catalog.py — TerraLens resource catalog
Contains the full AWS resource catalog, HCL resource templates,
provider list, and helper functions for the Add Resource wizard.
"""

from __future__ import annotations


# ─────────────────────────────────────────────
# Full AWS Resource Catalog
# ─────────────────────────────────────────────
AWS_RESOURCE_CATALOG: dict[str, list[dict]] = {
    "Compute": [
        {"type": "aws_instance",                        "description": "EC2 virtual machine"},
        {"type": "aws_launch_template",                 "description": "EC2 launch template"},
        {"type": "aws_launch_configuration",            "description": "EC2 launch configuration (legacy)"},
        {"type": "aws_autoscaling_group",               "description": "Auto Scaling group"},
        {"type": "aws_autoscaling_policy",              "description": "Auto Scaling scaling policy"},
        {"type": "aws_autoscaling_schedule",            "description": "Auto Scaling scheduled action"},
        {"type": "aws_spot_instance_request",           "description": "EC2 Spot instance request"},
        {"type": "aws_placement_group",                 "description": "EC2 placement group"},
        {"type": "aws_key_pair",                        "description": "EC2 SSH key pair"},
        {"type": "aws_ami",                             "description": "Amazon Machine Image"},
        {"type": "aws_ami_copy",                        "description": "Copy an AMI to another region"},
        {"type": "aws_ami_from_instance",               "description": "Create AMI from existing instance"},
        {"type": "aws_ebs_volume",                      "description": "EBS block storage volume"},
        {"type": "aws_ebs_snapshot",                    "description": "EBS volume snapshot"},
        {"type": "aws_ebs_snapshot_copy",               "description": "Copy EBS snapshot"},
        {"type": "aws_volume_attachment",               "description": "Attach EBS volume to instance"},
        {"type": "aws_eip",                             "description": "Elastic IP address"},
        {"type": "aws_eip_association",                 "description": "Associate EIP with instance"},
        {"type": "aws_dedicated_host",                  "description": "EC2 dedicated host"},
        {"type": "aws_capacity_reservation",            "description": "EC2 capacity reservation"},
    ],
    "Containers": [
        {"type": "aws_ecs_cluster",                     "description": "ECS container cluster"},
        {"type": "aws_ecs_service",                     "description": "ECS service (task runner)"},
        {"type": "aws_ecs_task_definition",             "description": "ECS task definition"},
        {"type": "aws_ecs_capacity_provider",           "description": "ECS capacity provider"},
        {"type": "aws_ecr_repository",                  "description": "ECR container image registry"},
        {"type": "aws_ecr_repository_policy",           "description": "ECR repository access policy"},
        {"type": "aws_ecr_lifecycle_policy",            "description": "ECR image lifecycle policy"},
        {"type": "aws_ecr_replication_configuration",   "description": "ECR cross-region replication"},
        {"type": "aws_eks_cluster",                     "description": "EKS Kubernetes cluster"},
        {"type": "aws_eks_node_group",                  "description": "EKS managed node group"},
        {"type": "aws_eks_fargate_profile",             "description": "EKS Fargate profile"},
        {"type": "aws_eks_addon",                       "description": "EKS cluster add-on"},
        {"type": "aws_eks_identity_provider_config",    "description": "EKS OIDC identity provider"},
    ],
    "Serverless": [
        {"type": "aws_lambda_function",                 "description": "Lambda serverless function"},
        {"type": "aws_lambda_alias",                    "description": "Lambda function alias"},
        {"type": "aws_lambda_event_source_mapping",     "description": "Lambda event source trigger"},
        {"type": "aws_lambda_function_url",             "description": "Lambda function URL endpoint"},
        {"type": "aws_lambda_layer_version",            "description": "Lambda layer (shared code)"},
        {"type": "aws_lambda_permission",               "description": "Lambda resource-based permission"},
        {"type": "aws_lambda_provisioned_concurrency_config", "description": "Lambda provisioned concurrency"},
        {"type": "aws_serverlessapplicationrepository_cloudformation_stack", "description": "SAR application stack"},
    ],
    "Storage": [
        {"type": "aws_s3_bucket",                       "description": "S3 object storage bucket"},
        {"type": "aws_s3_bucket_acl",                   "description": "S3 bucket ACL"},
        {"type": "aws_s3_bucket_cors_configuration",    "description": "S3 CORS configuration"},
        {"type": "aws_s3_bucket_lifecycle_configuration","description": "S3 lifecycle rules"},
        {"type": "aws_s3_bucket_logging",               "description": "S3 access logging"},
        {"type": "aws_s3_bucket_notification",          "description": "S3 event notifications"},
        {"type": "aws_s3_bucket_object",                "description": "S3 object (file upload)"},
        {"type": "aws_s3_bucket_policy",                "description": "S3 bucket resource policy"},
        {"type": "aws_s3_bucket_public_access_block",   "description": "S3 block public access settings"},
        {"type": "aws_s3_bucket_replication_configuration", "description": "S3 cross-region replication"},
        {"type": "aws_s3_bucket_server_side_encryption_configuration", "description": "S3 default encryption"},
        {"type": "aws_s3_bucket_versioning",            "description": "S3 bucket versioning"},
        {"type": "aws_s3_bucket_website_configuration", "description": "S3 static website hosting"},
        {"type": "aws_s3_object",                       "description": "S3 object (newer resource)"},
        {"type": "aws_efs_file_system",                 "description": "EFS elastic NFS file system"},
        {"type": "aws_efs_mount_target",                "description": "EFS mount target in subnet"},
        {"type": "aws_efs_access_point",                "description": "EFS application access point"},
        {"type": "aws_efs_backup_policy",               "description": "EFS backup policy"},
        {"type": "aws_fsx_lustre_file_system",          "description": "FSx for Lustre HPC file system"},
        {"type": "aws_fsx_windows_file_system",         "description": "FSx for Windows File Server"},
        {"type": "aws_fsx_ontap_file_system",           "description": "FSx for NetApp ONTAP"},
        {"type": "aws_glacier_vault",                   "description": "S3 Glacier archive vault"},
        {"type": "aws_storagegateway_gateway",          "description": "Storage Gateway appliance"},
    ],
    "Database": [
        {"type": "aws_db_instance",                     "description": "RDS managed relational database"},
        {"type": "aws_db_cluster",                      "description": "RDS Aurora cluster"},
        {"type": "aws_rds_cluster",                     "description": "Aurora Serverless cluster"},
        {"type": "aws_rds_cluster_instance",            "description": "Aurora cluster instance"},
        {"type": "aws_db_subnet_group",                 "description": "RDS subnet group"},
        {"type": "aws_db_parameter_group",              "description": "RDS database parameter group"},
        {"type": "aws_db_option_group",                 "description": "RDS database option group"},
        {"type": "aws_db_snapshot",                     "description": "RDS manual snapshot"},
        {"type": "aws_db_event_subscription",           "description": "RDS event notification"},
        {"type": "aws_dynamodb_table",                  "description": "DynamoDB NoSQL table"},
        {"type": "aws_dynamodb_global_table",           "description": "DynamoDB global (multi-region) table"},
        {"type": "aws_dynamodb_table_item",             "description": "DynamoDB table item"},
        {"type": "aws_elasticache_cluster",             "description": "ElastiCache Redis/Memcached cluster"},
        {"type": "aws_elasticache_replication_group",   "description": "ElastiCache Redis replication group"},
        {"type": "aws_elasticache_subnet_group",        "description": "ElastiCache subnet group"},
        {"type": "aws_elasticache_parameter_group",     "description": "ElastiCache parameter group"},
        {"type": "aws_redshift_cluster",                "description": "Redshift data warehouse cluster"},
        {"type": "aws_redshift_subnet_group",           "description": "Redshift subnet group"},
        {"type": "aws_redshift_parameter_group",        "description": "Redshift parameter group"},
        {"type": "aws_neptune_cluster",                 "description": "Neptune graph database cluster"},
        {"type": "aws_neptune_cluster_instance",        "description": "Neptune cluster instance"},
        {"type": "aws_docdb_cluster",                   "description": "DocumentDB (MongoDB-compatible) cluster"},
        {"type": "aws_docdb_cluster_instance",          "description": "DocumentDB cluster instance"},
        {"type": "aws_timestreaminfluxdb_db_instance",  "description": "Timestream InfluxDB instance"},
        {"type": "aws_memorydb_cluster",                "description": "MemoryDB for Redis cluster"},
        {"type": "aws_keyspaces_table",                 "description": "Keyspaces (Cassandra) table"},
        {"type": "aws_opensearch_domain",               "description": "OpenSearch Service domain"},
    ],
    "Networking": [
        {"type": "aws_vpc",                             "description": "Virtual Private Cloud"},
        {"type": "aws_subnet",                          "description": "VPC subnet"},
        {"type": "aws_internet_gateway",                "description": "VPC internet gateway"},
        {"type": "aws_nat_gateway",                     "description": "NAT gateway for private subnets"},
        {"type": "aws_route_table",                     "description": "VPC route table"},
        {"type": "aws_route",                           "description": "Individual VPC route"},
        {"type": "aws_route_table_association",         "description": "Associate route table with subnet"},
        {"type": "aws_security_group",                  "description": "EC2/VPC security group"},
        {"type": "aws_security_group_rule",             "description": "Individual security group rule"},
        {"type": "aws_vpc_peering_connection",          "description": "VPC peering connection"},
        {"type": "aws_vpc_endpoint",                    "description": "VPC endpoint for AWS services"},
        {"type": "aws_vpc_endpoint_service",            "description": "VPC endpoint service (PrivateLink)"},
        {"type": "aws_network_acl",                     "description": "VPC Network ACL"},
        {"type": "aws_network_acl_rule",                "description": "Network ACL rule"},
        {"type": "aws_vpn_gateway",                     "description": "VPN gateway"},
        {"type": "aws_vpn_connection",                  "description": "Site-to-site VPN connection"},
        {"type": "aws_customer_gateway",                "description": "Customer gateway for VPN"},
        {"type": "aws_dx_connection",                   "description": "AWS Direct Connect connection"},
        {"type": "aws_dx_gateway",                      "description": "Direct Connect gateway"},
        {"type": "aws_dx_virtual_interface",            "description": "Direct Connect virtual interface"},
        {"type": "aws_transit_gateway",                 "description": "Transit Gateway (hub routing)"},
        {"type": "aws_transit_gateway_vpc_attachment",  "description": "Transit Gateway VPC attachment"},
        {"type": "aws_transit_gateway_route_table",     "description": "Transit Gateway route table"},
        {"type": "aws_flow_log",                        "description": "VPC flow log"},
        {"type": "aws_network_interface",               "description": "Elastic Network Interface"},
        {"type": "aws_egress_only_internet_gateway",    "description": "Egress-only internet gateway (IPv6)"},
    ],
    "Load Balancing": [
        {"type": "aws_lb",                              "description": "Application/Network Load Balancer"},
        {"type": "aws_alb",                             "description": "Application Load Balancer (alias)"},
        {"type": "aws_lb_listener",                     "description": "ALB/NLB listener"},
        {"type": "aws_lb_listener_rule",                "description": "ALB listener routing rule"},
        {"type": "aws_lb_target_group",                 "description": "ALB/NLB target group"},
        {"type": "aws_lb_target_group_attachment",      "description": "Register target with target group"},
        {"type": "aws_elb",                             "description": "Classic Load Balancer (legacy)"},
        {"type": "aws_app_cookie_stickiness_policy",    "description": "ELB app cookie stickiness"},
        {"type": "aws_proxy_protocol_policy",           "description": "ELB proxy protocol policy"},
    ],
    "DNS & CDN": [
        {"type": "aws_route53_zone",                    "description": "Route 53 hosted DNS zone"},
        {"type": "aws_route53_record",                  "description": "Route 53 DNS record"},
        {"type": "aws_route53_health_check",            "description": "Route 53 health check"},
        {"type": "aws_route53_delegation_set",          "description": "Route 53 reusable delegation set"},
        {"type": "aws_route53_query_log",               "description": "Route 53 query logging"},
        {"type": "aws_route53_resolver_endpoint",       "description": "Route 53 Resolver endpoint"},
        {"type": "aws_route53_resolver_rule",           "description": "Route 53 Resolver forwarding rule"},
        {"type": "aws_cloudfront_distribution",         "description": "CloudFront CDN distribution"},
        {"type": "aws_cloudfront_cache_policy",         "description": "CloudFront cache policy"},
        {"type": "aws_cloudfront_origin_access_identity","description": "CloudFront OAI for S3"},
        {"type": "aws_cloudfront_origin_request_policy","description": "CloudFront origin request policy"},
        {"type": "aws_cloudfront_function",             "description": "CloudFront edge function"},
        {"type": "aws_cloudfront_realtime_log_config",  "description": "CloudFront real-time logs"},
        {"type": "aws_globalaccelerator_accelerator",   "description": "Global Accelerator"},
        {"type": "aws_globalaccelerator_endpoint_group","description": "Global Accelerator endpoint group"},
        {"type": "aws_globalaccelerator_listener",      "description": "Global Accelerator listener"},
    ],
    "IAM & Security": [
        {"type": "aws_iam_user",                        "description": "IAM user"},
        {"type": "aws_iam_user_policy",                 "description": "IAM inline user policy"},
        {"type": "aws_iam_user_policy_attachment",      "description": "Attach managed policy to user"},
        {"type": "aws_iam_user_login_profile",          "description": "IAM user console login profile"},
        {"type": "aws_iam_access_key",                  "description": "IAM user access key"},
        {"type": "aws_iam_group",                       "description": "IAM group"},
        {"type": "aws_iam_group_membership",            "description": "IAM group membership"},
        {"type": "aws_iam_group_policy",                "description": "IAM inline group policy"},
        {"type": "aws_iam_group_policy_attachment",     "description": "Attach managed policy to group"},
        {"type": "aws_iam_role",                        "description": "IAM role"},
        {"type": "aws_iam_role_policy",                 "description": "IAM inline role policy"},
        {"type": "aws_iam_role_policy_attachment",      "description": "Attach managed policy to role"},
        {"type": "aws_iam_policy",                      "description": "IAM managed policy"},
        {"type": "aws_iam_instance_profile",            "description": "IAM instance profile for EC2"},
        {"type": "aws_iam_openid_connect_provider",     "description": "IAM OIDC identity provider"},
        {"type": "aws_iam_saml_provider",               "description": "IAM SAML identity provider"},
        {"type": "aws_iam_server_certificate",          "description": "IAM SSL/TLS certificate"},
        {"type": "aws_iam_account_password_policy",     "description": "IAM account password policy"},
        {"type": "aws_iam_account_alias",               "description": "IAM account alias"},
        {"type": "aws_kms_key",                         "description": "KMS encryption key"},
        {"type": "aws_kms_alias",                       "description": "KMS key alias"},
        {"type": "aws_kms_grant",                       "description": "KMS key grant"},
        {"type": "aws_secretsmanager_secret",           "description": "Secrets Manager secret"},
        {"type": "aws_secretsmanager_secret_version",   "description": "Secrets Manager secret value"},
        {"type": "aws_secretsmanager_secret_rotation",  "description": "Secrets Manager rotation config"},
        {"type": "aws_ssm_parameter",                   "description": "SSM Parameter Store value"},
        {"type": "aws_ssm_document",                    "description": "SSM automation/run document"},
        {"type": "aws_acm_certificate",                 "description": "ACM SSL/TLS certificate"},
        {"type": "aws_acm_certificate_validation",      "description": "ACM certificate DNS validation"},
        {"type": "aws_wafv2_web_acl",                   "description": "WAFv2 Web ACL"},
        {"type": "aws_wafv2_ip_set",                    "description": "WAFv2 IP set"},
        {"type": "aws_wafv2_regex_pattern_set",         "description": "WAFv2 regex pattern set"},
        {"type": "aws_wafv2_rule_group",                "description": "WAFv2 rule group"},
        {"type": "aws_shield_protection",               "description": "AWS Shield DDoS protection"},
        {"type": "aws_guardduty_detector",              "description": "GuardDuty threat detection"},
        {"type": "aws_guardduty_member",                "description": "GuardDuty member account"},
        {"type": "aws_inspector2_enabler",              "description": "Inspector v2 vulnerability scanning"},
        {"type": "aws_macie2_account",                  "description": "Macie data security/discovery"},
        {"type": "aws_securityhub_account",             "description": "Security Hub aggregation"},
        {"type": "aws_detective_graph",                 "description": "Detective security investigation"},
        {"type": "aws_cognito_user_pool",               "description": "Cognito user pool"},
        {"type": "aws_cognito_user_pool_client",        "description": "Cognito app client"},
        {"type": "aws_cognito_identity_pool",           "description": "Cognito identity pool (federated)"},
    ],
    "Messaging & Queuing": [
        {"type": "aws_sqs_queue",                       "description": "SQS message queue"},
        {"type": "aws_sqs_queue_policy",                "description": "SQS queue access policy"},
        {"type": "aws_sqs_queue_redrive_policy",        "description": "SQS dead-letter queue policy"},
        {"type": "aws_sns_topic",                       "description": "SNS notification topic"},
        {"type": "aws_sns_topic_subscription",          "description": "SNS topic subscription"},
        {"type": "aws_sns_topic_policy",                "description": "SNS topic access policy"},
        {"type": "aws_mq_broker",                       "description": "Amazon MQ message broker"},
        {"type": "aws_mq_configuration",                "description": "Amazon MQ broker configuration"},
        {"type": "aws_kinesis_stream",                  "description": "Kinesis data stream"},
        {"type": "aws_kinesis_firehose_delivery_stream","description": "Kinesis Firehose delivery stream"},
        {"type": "aws_kinesis_analytics_application",   "description": "Kinesis Analytics (SQL) application"},
        {"type": "aws_kinesisanalyticsv2_application",  "description": "Kinesis Analytics v2 (Flink) app"},
        {"type": "aws_kafka_cluster",                   "description": "MSK Apache Kafka cluster"},
        {"type": "aws_msk_cluster",                     "description": "MSK cluster (alias)"},
        {"type": "aws_msk_configuration",               "description": "MSK broker configuration"},
        {"type": "aws_eventbridge_bus",                 "description": "EventBridge custom event bus"},
        {"type": "aws_cloudwatch_event_bus",            "description": "CloudWatch Events bus (legacy)"},
        {"type": "aws_cloudwatch_event_rule",           "description": "EventBridge/CloudWatch event rule"},
        {"type": "aws_cloudwatch_event_target",         "description": "EventBridge event target"},
        {"type": "aws_pipes_pipe",                      "description": "EventBridge Pipes event pipeline"},
    ],
    "Monitoring & Logging": [
        {"type": "aws_cloudwatch_metric_alarm",         "description": "CloudWatch metric alarm"},
        {"type": "aws_cloudwatch_composite_alarm",      "description": "CloudWatch composite alarm"},
        {"type": "aws_cloudwatch_dashboard",            "description": "CloudWatch dashboard"},
        {"type": "aws_cloudwatch_log_group",            "description": "CloudWatch Logs log group"},
        {"type": "aws_cloudwatch_log_stream",           "description": "CloudWatch Logs log stream"},
        {"type": "aws_cloudwatch_log_metric_filter",    "description": "CloudWatch Logs metric filter"},
        {"type": "aws_cloudwatch_log_subscription_filter","description": "CloudWatch Logs subscription"},
        {"type": "aws_cloudwatch_log_destination",      "description": "CloudWatch Logs destination"},
        {"type": "aws_cloudwatch_log_resource_policy",  "description": "CloudWatch Logs resource policy"},
        {"type": "aws_cloudwatch_metric_stream",        "description": "CloudWatch metric stream"},
        {"type": "aws_xray_group",                      "description": "X-Ray trace group"},
        {"type": "aws_xray_sampling_rule",              "description": "X-Ray sampling rule"},
        {"type": "aws_cloudtrail",                      "description": "CloudTrail audit log trail"},
        {"type": "aws_cloudtrail_event_data_store",     "description": "CloudTrail Lake event data store"},
        {"type": "aws_config_config_rule",              "description": "AWS Config compliance rule"},
        {"type": "aws_config_configuration_recorder",   "description": "AWS Config recorder"},
        {"type": "aws_config_delivery_channel",         "description": "AWS Config delivery channel"},
        {"type": "aws_config_conformance_pack",         "description": "AWS Config conformance pack"},
    ],
    "API & Integration": [
        {"type": "aws_api_gateway_rest_api",            "description": "API Gateway REST API"},
        {"type": "aws_api_gateway_resource",            "description": "API Gateway resource path"},
        {"type": "aws_api_gateway_method",              "description": "API Gateway HTTP method"},
        {"type": "aws_api_gateway_integration",         "description": "API Gateway backend integration"},
        {"type": "aws_api_gateway_deployment",          "description": "API Gateway deployment"},
        {"type": "aws_api_gateway_stage",               "description": "API Gateway stage (env)"},
        {"type": "aws_api_gateway_authorizer",          "description": "API Gateway Lambda/Cognito auth"},
        {"type": "aws_api_gateway_domain_name",         "description": "API Gateway custom domain"},
        {"type": "aws_api_gateway_usage_plan",          "description": "API Gateway usage plan"},
        {"type": "aws_api_gateway_api_key",             "description": "API Gateway API key"},
        {"type": "aws_apigatewayv2_api",                "description": "API Gateway v2 (HTTP/WebSocket API)"},
        {"type": "aws_apigatewayv2_stage",              "description": "API Gateway v2 stage"},
        {"type": "aws_apigatewayv2_route",              "description": "API Gateway v2 route"},
        {"type": "aws_apigatewayv2_integration",        "description": "API Gateway v2 integration"},
        {"type": "aws_apigatewayv2_authorizer",         "description": "API Gateway v2 authorizer"},
        {"type": "aws_apigatewayv2_domain_name",        "description": "API Gateway v2 custom domain"},
        {"type": "aws_appsync_graphql_api",             "description": "AppSync GraphQL API"},
        {"type": "aws_appsync_datasource",              "description": "AppSync data source"},
        {"type": "aws_appsync_resolver",                "description": "AppSync resolver"},
        {"type": "aws_sfn_state_machine",               "description": "Step Functions state machine"},
        {"type": "aws_sfn_activity",                    "description": "Step Functions activity"},
    ],
    "DevOps & CI/CD": [
        {"type": "aws_codebuild_project",               "description": "CodeBuild CI build project"},
        {"type": "aws_codebuild_report_group",          "description": "CodeBuild test report group"},
        {"type": "aws_codecommit_repository",           "description": "CodeCommit Git repository"},
        {"type": "aws_codedeploy_app",                  "description": "CodeDeploy application"},
        {"type": "aws_codedeploy_deployment_config",    "description": "CodeDeploy deployment config"},
        {"type": "aws_codedeploy_deployment_group",     "description": "CodeDeploy deployment group"},
        {"type": "aws_codepipeline",                    "description": "CodePipeline CI/CD pipeline"},
        {"type": "aws_codepipeline_webhook",            "description": "CodePipeline webhook trigger"},
        {"type": "aws_codeartifact_domain",             "description": "CodeArtifact artifact domain"},
        {"type": "aws_codeartifact_repository",         "description": "CodeArtifact package repository"},
        {"type": "aws_codestar_connections_connection",  "description": "CodeStar GitHub/GitLab connection"},
        {"type": "aws_codestar_notifications_notification_rule", "description": "CodeStar notification rule"},
        {"type": "aws_cloudformation_stack",            "description": "CloudFormation stack"},
        {"type": "aws_cloudformation_stack_set",        "description": "CloudFormation StackSet"},
        {"type": "aws_service_catalog_portfolio",       "description": "Service Catalog portfolio"},
        {"type": "aws_service_catalog_product",         "description": "Service Catalog product"},
    ],
    "Machine Learning": [
        {"type": "aws_sagemaker_domain",                "description": "SageMaker Studio domain"},
        {"type": "aws_sagemaker_model",                 "description": "SageMaker ML model"},
        {"type": "aws_sagemaker_endpoint",              "description": "SageMaker inference endpoint"},
        {"type": "aws_sagemaker_endpoint_configuration","description": "SageMaker endpoint config"},
        {"type": "aws_sagemaker_notebook_instance",     "description": "SageMaker Jupyter notebook"},
        {"type": "aws_sagemaker_training_job",          "description": "SageMaker training job"},
        {"type": "aws_sagemaker_feature_group",         "description": "SageMaker Feature Store group"},
        {"type": "aws_sagemaker_pipeline",              "description": "SageMaker ML pipeline"},
        {"type": "aws_bedrock_model_invocation_logging_configuration", "description": "Bedrock model logging"},
        {"type": "aws_bedrockagent_agent",              "description": "Bedrock Agent"},
        {"type": "aws_bedrockagent_knowledge_base",     "description": "Bedrock knowledge base"},
        {"type": "aws_rekognition_collection",          "description": "Rekognition image collection"},
        {"type": "aws_lexv2models_bot",                 "description": "Lex v2 conversational bot"},
        {"type": "aws_comprehend_entity_recognizer",    "description": "Comprehend entity recognizer"},
        {"type": "aws_translate_parallel_data",         "description": "Translate parallel data"},
    ],
    "Data & Analytics": [
        {"type": "aws_glue_catalog_database",           "description": "Glue Data Catalog database"},
        {"type": "aws_glue_catalog_table",              "description": "Glue Data Catalog table"},
        {"type": "aws_glue_job",                        "description": "Glue ETL job"},
        {"type": "aws_glue_crawler",                    "description": "Glue data crawler"},
        {"type": "aws_glue_connection",                 "description": "Glue data store connection"},
        {"type": "aws_glue_trigger",                    "description": "Glue workflow trigger"},
        {"type": "aws_glue_workflow",                   "description": "Glue orchestration workflow"},
        {"type": "aws_athena_database",                 "description": "Athena query database"},
        {"type": "aws_athena_workgroup",                "description": "Athena query workgroup"},
        {"type": "aws_athena_named_query",              "description": "Athena saved query"},
        {"type": "aws_emr_cluster",                     "description": "EMR Hadoop/Spark cluster"},
        {"type": "aws_emr_serverless_application",      "description": "EMR Serverless application"},
        {"type": "aws_lakeformation_resource",          "description": "Lake Formation data lake resource"},
        {"type": "aws_lakeformation_permissions",       "description": "Lake Formation permissions"},
        {"type": "aws_quicksight_user",                 "description": "QuickSight BI user"},
        {"type": "aws_quicksight_data_source",          "description": "QuickSight data source"},
        {"type": "aws_datapipeline_pipeline",           "description": "Data Pipeline workflow"},
    ],
    "IoT": [
        {"type": "aws_iot_thing",                       "description": "IoT device thing"},
        {"type": "aws_iot_thing_type",                  "description": "IoT thing type"},
        {"type": "aws_iot_certificate",                 "description": "IoT device certificate"},
        {"type": "aws_iot_policy",                      "description": "IoT device policy"},
        {"type": "aws_iot_topic_rule",                  "description": "IoT message routing rule"},
        {"type": "aws_iot_role_alias",                  "description": "IoT role alias"},
        {"type": "aws_iotevents_detector_model",        "description": "IoT Events detector model"},
        {"type": "aws_iotanalytics_channel",            "description": "IoT Analytics channel"},
    ],
    "Application Services": [
        {"type": "aws_elastic_beanstalk_application",   "description": "Elastic Beanstalk application"},
        {"type": "aws_elastic_beanstalk_environment",   "description": "Elastic Beanstalk environment"},
        {"type": "aws_lightsail_instance",              "description": "Lightsail VPS instance"},
        {"type": "aws_lightsail_static_ip",             "description": "Lightsail static IP"},
        {"type": "aws_lightsail_domain",                "description": "Lightsail DNS domain"},
        {"type": "aws_amplify_app",                     "description": "Amplify full-stack app"},
        {"type": "aws_amplify_branch",                  "description": "Amplify app branch"},
        {"type": "aws_apprunner_service",               "description": "App Runner containerized service"},
        {"type": "aws_apprunner_auto_scaling_configuration_version", "description": "App Runner autoscaling"},
        {"type": "aws_batch_job_definition",            "description": "Batch job definition"},
        {"type": "aws_batch_job_queue",                 "description": "Batch job queue"},
        {"type": "aws_batch_compute_environment",       "description": "Batch compute environment"},
    ],
    "Cost & Billing": [
        {"type": "aws_budgets_budget",                  "description": "AWS budget with alerts"},
        {"type": "aws_ce_cost_category",                "description": "Cost Explorer cost category"},
        {"type": "aws_cur_report_definition",           "description": "Cost & Usage Report definition"},
        {"type": "aws_savingsplans_savings_plan",        "description": "Savings Plan commitment"},
    ],
    "Migration": [
        {"type": "aws_dms_replication_instance",        "description": "DMS database migration instance"},
        {"type": "aws_dms_endpoint",                    "description": "DMS source/target endpoint"},
        {"type": "aws_dms_replication_task",            "description": "DMS migration replication task"},
        {"type": "aws_datasync_agent",                  "description": "DataSync transfer agent"},
        {"type": "aws_datasync_task",                   "description": "DataSync transfer task"},
        {"type": "aws_migration_hub_config",            "description": "Migration Hub home region config"},
    ],
    "Management": [
        {"type": "aws_organizations_organization",      "description": "AWS Organizations root"},
        {"type": "aws_organizations_account",           "description": "AWS Organizations member account"},
        {"type": "aws_organizations_policy",            "description": "Organizations SCP policy"},
        {"type": "aws_organizations_policy_attachment", "description": "Attach SCP to OU/account"},
        {"type": "aws_ram_resource_share",              "description": "RAM cross-account resource share"},
        {"type": "aws_ram_resource_association",        "description": "RAM resource association"},
        {"type": "aws_resourcegroups_group",            "description": "Resource Groups tag-based group"},
        {"type": "aws_ssm_maintenance_window",          "description": "SSM maintenance window"},
        {"type": "aws_ssm_patch_baseline",              "description": "SSM patch management baseline"},
        {"type": "aws_service_quotas_service_quota",    "description": "Service Quotas limit request"},
        {"type": "aws_account_alternate_contact",       "description": "Account alternate contact"},
        {"type": "aws_iam_service_linked_role",         "description": "IAM service-linked role"},
    ],
}

# Flatten catalog for search, deduplicating by type (keep first occurrence)
_seen_types: set[str] = set()
ALL_AWS_RESOURCES: list[dict] = []
for _cat, _resources in AWS_RESOURCE_CATALOG.items():
    for _r in _resources:
        if _r["type"] not in _seen_types:
            _seen_types.add(_r["type"])
            ALL_AWS_RESOURCES.append({"type": _r["type"], "description": _r["description"], "category": _cat})


# ─────────────────────────────────────────────
# Provider list
# ─────────────────────────────────────────────
PROVIDERS = [
    {"id": "aws",        "name": "Amazon Web Services",  "icon": "🟠", "supported": True},
    {"id": "azure",      "name": "Microsoft Azure",       "icon": "🔵", "supported": False},
    {"id": "gcp",        "name": "Google Cloud Platform", "icon": "🔴", "supported": False},
    {"id": "oracle",     "name": "Oracle Cloud",          "icon": "🟤", "supported": False},
    {"id": "docker",     "name": "Docker",                "icon": "🐳", "supported": False},
    {"id": "kubernetes", "name": "Kubernetes",            "icon": "☸️",  "supported": False},
]


# ─────────────────────────────────────────────
# HCL Resource Templates
# ─────────────────────────────────────────────
RESOURCE_TEMPLATES: dict[str, dict] = {
    "aws_s3_bucket": {
        "description": "S3 object storage bucket",
        "fields": [
            {"name": "resource_name", "label": "Resource name (TF identifier)", "placeholder": "my_bucket", "required": True, "default": ""},
            {"name": "bucket",        "label": "Bucket name (globally unique)",  "placeholder": "my-unique-bucket-name", "required": True, "default": ""},
            {"name": "tags_name",     "label": "Tag: Name",                       "placeholder": "MyBucket", "required": False, "default": ""},
        ],
        "template": '''resource "aws_s3_bucket" "{resource_name}" {{
  bucket = "{bucket}"{tags_block}
}}
''',
    },
    "aws_instance": {
        "description": "EC2 virtual machine",
        "fields": [
            {"name": "resource_name",   "label": "Resource name (TF identifier)", "placeholder": "web_server",            "required": True,  "default": ""},
            {"name": "ami",             "label": "AMI ID",                         "placeholder": "ami-0c55b159cbfafe1f0", "required": True,  "default": ""},
            {"name": "instance_type",   "label": "Instance type",                  "placeholder": "t3.micro",              "required": True,  "default": "t3.micro"},
            {"name": "tags_name",       "label": "Tag: Name",                      "placeholder": "WebServer",             "required": False, "default": ""},
        ],
        "template": '''resource "aws_instance" "{resource_name}" {{
  ami           = "{ami}"
  instance_type = "{instance_type}"{tags_block}
}}
''',
    },
    "aws_vpc": {
        "description": "Virtual Private Cloud network",
        "fields": [
            {"name": "resource_name",          "label": "Resource name (TF identifier)", "placeholder": "main",         "required": True,  "default": "main"},
            {"name": "cidr_block",             "label": "CIDR block",                    "placeholder": "10.0.0.0/16",  "required": True,  "default": "10.0.0.0/16"},
            {"name": "enable_dns_hostnames",   "label": "Enable DNS hostnames (true/false)", "placeholder": "true",    "required": False, "default": "true"},
            {"name": "tags_name",              "label": "Tag: Name",                     "placeholder": "MainVPC",      "required": False, "default": ""},
        ],
        "template": '''resource "aws_vpc" "{resource_name}" {{
  cidr_block           = "{cidr_block}"
  enable_dns_hostnames = {enable_dns_hostnames}{tags_block}
}}
''',
    },
    "aws_subnet": {
        "description": "Subnet within a VPC",
        "fields": [
            {"name": "resource_name",       "label": "Resource name (TF identifier)", "placeholder": "public_subnet_1",   "required": True,  "default": ""},
            {"name": "vpc_id",              "label": "VPC ID or reference",           "placeholder": "aws_vpc.main.id",   "required": True,  "default": ""},
            {"name": "cidr_block",          "label": "CIDR block",                    "placeholder": "10.0.1.0/24",       "required": True,  "default": ""},
            {"name": "availability_zone",   "label": "Availability zone",             "placeholder": "us-east-1a",        "required": False, "default": ""},
            {"name": "tags_name",           "label": "Tag: Name",                     "placeholder": "PublicSubnet1",     "required": False, "default": ""},
        ],
        "template": '''resource "aws_subnet" "{resource_name}" {{
  vpc_id            = {vpc_id}
  cidr_block        = "{cidr_block}"{az_block}{tags_block}
}}
''',
    },
    "aws_security_group": {
        "description": "EC2 security group (firewall rules)",
        "fields": [
            {"name": "resource_name", "label": "Resource name (TF identifier)", "placeholder": "web_sg",                 "required": True,  "default": ""},
            {"name": "name",          "label": "Security group name",            "placeholder": "web-security-group",     "required": True,  "default": ""},
            {"name": "description",   "label": "Description",                    "placeholder": "Security group for web", "required": True,  "default": ""},
            {"name": "vpc_id",        "label": "VPC ID or reference",            "placeholder": "aws_vpc.main.id",        "required": False, "default": ""},
            {"name": "tags_name",     "label": "Tag: Name",                      "placeholder": "WebSG",                  "required": False, "default": ""},
        ],
        "template": '''resource "aws_security_group" "{resource_name}" {{
  name        = "{name}"
  description = "{description}"{vpc_block}{tags_block}
}}
''',
    },
    "aws_db_instance": {
        "description": "RDS managed database",
        "fields": [
            {"name": "resource_name",      "label": "Resource name (TF identifier)", "placeholder": "main_db",       "required": True,  "default": ""},
            {"name": "identifier",         "label": "DB identifier",                  "placeholder": "main-db-prod",  "required": True,  "default": ""},
            {"name": "engine",             "label": "Engine",                         "placeholder": "postgres",      "required": True,  "default": "postgres"},
            {"name": "engine_version",     "label": "Engine version",                 "placeholder": "14",            "required": True,  "default": "14"},
            {"name": "instance_class",     "label": "Instance class",                 "placeholder": "db.t3.micro",   "required": True,  "default": "db.t3.micro"},
            {"name": "allocated_storage",  "label": "Allocated storage (GB)",         "placeholder": "20",            "required": True,  "default": "20"},
            {"name": "db_name",            "label": "Database name",                  "placeholder": "mydb",          "required": True,  "default": ""},
            {"name": "username",           "label": "Master username",                "placeholder": "admin",         "required": True,  "default": "admin"},
            {"name": "password",           "label": "Master password",                "placeholder": "changeme123",   "required": True,  "default": ""},
        ],
        "template": '''resource "aws_db_instance" "{resource_name}" {{
  identifier        = "{identifier}"
  engine            = "{engine}"
  engine_version    = "{engine_version}"
  instance_class    = "{instance_class}"
  allocated_storage = {allocated_storage}
  db_name           = "{db_name}"
  username          = "{username}"
  password          = "{password}"
  skip_final_snapshot = true
}}
''',
    },
    "aws_iam_role": {
        "description": "IAM role for AWS service permissions",
        "fields": [
            {"name": "resource_name", "label": "Resource name (TF identifier)", "placeholder": "lambda_role",         "required": True,  "default": ""},
            {"name": "name",          "label": "IAM role name",                  "placeholder": "lambda-exec-role",    "required": True,  "default": ""},
            {"name": "service",       "label": "AWS service principal",           "placeholder": "lambda.amazonaws.com","required": True,  "default": "lambda.amazonaws.com"},
            {"name": "tags_name",     "label": "Tag: Name",                      "placeholder": "LambdaRole",          "required": False, "default": ""},
        ],
        "template": '''resource "aws_iam_role" "{resource_name}" {{
  name = "{name}"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {{ Service = "{service}" }}
    }}]
  }}){tags_block}
}}
''',
    },
    "aws_lambda_function": {
        "description": "Serverless Lambda function",
        "fields": [
            {"name": "resource_name",  "label": "Resource name (TF identifier)", "placeholder": "my_lambda",          "required": True,  "default": ""},
            {"name": "function_name",  "label": "Function name",                  "placeholder": "my-lambda-function", "required": True,  "default": ""},
            {"name": "runtime",        "label": "Runtime",                         "placeholder": "python3.11",         "required": True,  "default": "python3.11"},
            {"name": "handler",        "label": "Handler",                         "placeholder": "index.handler",      "required": True,  "default": "index.handler"},
            {"name": "role",           "label": "IAM role ARN or reference",       "placeholder": "aws_iam_role.lambda_role.arn", "required": True, "default": ""},
            {"name": "filename",       "label": "ZIP filename",                    "placeholder": "lambda.zip",         "required": True,  "default": "lambda.zip"},
        ],
        "template": '''resource "aws_lambda_function" "{resource_name}" {{
  function_name = "{function_name}"
  runtime       = "{runtime}"
  handler       = "{handler}"
  role          = {role}
  filename      = "{filename}"
}}
''',
    },
}


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
def _cat_id(cat: str) -> str:
    """Convert category name to a valid Textual widget ID."""
    return "cat-" + cat.replace(" ", "_").replace("&", "and").replace("/", "_")


def _build_tf_block(rtype: str, values: dict[str, str]) -> str:
    """Render a Terraform resource block from template + user values."""
    tmpl = RESOURCE_TEMPLATES[rtype]["template"]

    tags_name = values.get("tags_name", "").strip()
    if tags_name:
        values["tags_block"] = f'\n\n  tags = {{\n    Name = "{tags_name}"\n  }}'
    else:
        values["tags_block"] = ""

    az = values.get("availability_zone", "").strip()
    values["az_block"] = f'\n  availability_zone = "{az}"' if az else ""

    vpc = values.get("vpc_id", "").strip()
    values["vpc_block"] = f'\n  vpc_id = {vpc}' if vpc else ""

    dns = values.get("enable_dns_hostnames", "true").strip() or "true"
    values["enable_dns_hostnames"] = dns

    return tmpl.format(**values)
