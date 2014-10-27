#!/bin/sh

SHA1=$1
docker push sagebrew/sb_web:$SHA1
docker push sagebrew/sb_worker:$SHA1
EB_BUCKET=sagebrew-$CIRCLE_BRANCH/$DOCKER_CONFIG_BUCKET
DOCKERRUN_FILE_WEB=$SHA1-staging_Docker_web.aws.json
DOCKERRUN_FILE_WORKER=$SHA1-staging_Docker_worker.aws.json
DOCKERRUN_WEB_ENVIRONMENT=$SHA1-staging_Docker_web_environment.txt
DOCKERRUN_WORKER_ENVIRONMENT=$SHA1-staging_Docker_worker_environment.txt

sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_worker/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.worker_template > $DOCKERRUN_FILE_WORKER
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_web/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_WEB

sed "s/<APP_USER>/$APP_USER/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<REPO_NAME>/$REPO_NAME/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<PROJECT_NAME>/$PROJECT_NAME/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<LOG_ACCOUNT>/$LOG_ACCOUNT/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<LOG_TOKEN>/$LOG_TOKEN/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<CIRCLE_BRANCH>/$CIRCLE_BRANCH/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<APPLICATION_SECRET_KEY>/$APPLICATION_SECRET_KEY/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<BOMBERMAN_API_KEY>/$BOMBERMAN_API_KEY/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<SSL_CERT_LOCATION>/$SSL_CERT_LOCATION/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<SSL_KEY_LOCATION>/$SSL_KEY_LOCATION/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<AWS_S3_BUCKET>/$AWS_S3_BUCKET/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<AWS_SECRET_ACCESS_KEY>/$AWS_SECRET_ACCESS_KEY/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ALCHEMY_API_KEY>/$ALCHEMY_API_KEY/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ADDRESS_VALIDATION_ID>/$ADDRESS_VALIDATION_ID/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ADDRESS_VALIDATION_TOKEN>/$ADDRESS_VALIDATION_TOKEN/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_HOST>/$ELASTIC_SEARCH_HOST/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_PORT>/$ELASTIC_SEARCH_PORT/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_USER>/$ELASTIC_SEARCH_USER/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_KEY>/$ELASTIC_SEARCH_KEY/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<REDIS_LOCATION>/$REDIS_LOCATION/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<REDIS_PORT>/$REDIS_PORT/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<QUEUE_USERNAME>/$QUEUE_USERNAME/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<QUEUE_PASSWORD>/$QUEUE_PASSWORD/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<QUEUE_HOST>/$QUEUE_HOST/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT
sed "s/<QUEUE_PORT>/$QUEUE_PORT/;" < ~/com.sagebrew.web/aws_environment_config/web_environment_template.config > $DOCKERRUN_WEB_ENVIRONMENT


sed "s/<APP_USER>/$APP_USER/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<REPO_NAME>/$REPO_NAME/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<PROJECT_NAME>/$PROJECT_NAME/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<LOG_ACCOUNT>/$LOG_ACCOUNT/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<LOG_TOKEN>/$LOG_TOKEN/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<CIRCLE_BRANCH>/$CIRCLE_BRANCH/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<APPLICATION_SECRET_KEY>/$APPLICATION_SECRET_KEY/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<BOMBERMAN_API_KEY>/$BOMBERMAN_API_KEY/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<SSL_CERT_LOCATION>/$SSL_CERT_LOCATION/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<SSL_KEY_LOCATION>/$SSL_KEY_LOCATION/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<AWS_S3_BUCKET>/$AWS_S3_BUCKET/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<AWS_SECRET_ACCESS_KEY>/$AWS_SECRET_ACCESS_KEY/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ALCHEMY_API_KEY>/$ALCHEMY_API_KEY/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ADDRESS_VALIDATION_ID>/$ADDRESS_VALIDATION_ID/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ADDRESS_VALIDATION_TOKEN>/$ADDRESS_VALIDATION_TOKEN/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_HOST>/$ELASTIC_SEARCH_HOST/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_PORT>/$ELASTIC_SEARCH_PORT/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_USER>/$ELASTIC_SEARCH_USER/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<ELASTIC_SEARCH_KEY>/$ELASTIC_SEARCH_KEY/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<REDIS_LOCATION>/$REDIS_LOCATION/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<REDIS_PORT>/$REDIS_PORT/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<QUEUE_USERNAME>/$QUEUE_USERNAME/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<QUEUE_PASSWORD>/$QUEUE_PASSWORD/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<QUEUE_HOST>/$QUEUE_HOST/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT
sed "s/<QUEUE_PORT>/$QUEUE_PORT/;" < ~/com.sagebrew.web/aws_environment_config/worker_environment_template.config > $DOCKERRUN_WORKER_ENVIRONMENT



aws s3 cp $DOCKERRUN_FILE_WEB s3://$EB_BUCKET/$DOCKERRUN_FILE_WEB

#/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb

aws elasticbeanstalk create-application-version --application-name staging-web \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE_WEB

aws elasticbeanstalk update-environment --environment-name sagebrew-staging \
    --version-label $SHA1 -f $DOCKERRUN_WEB_ENVIRONMENT




aws s3 cp $DOCKERRUN_FILE_WORKER s3://$EB_BUCKET/$DOCKERRUN_FILE_WORKER

#/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb

aws elasticbeanstalk create-application-version --application-name staging-worker \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE_WORKER

aws elasticbeanstalk update-environment --environment-name sagebrew-staging-worker \
    --version-label $SHA1 -f $DOCKERRUN_WORKER_ENVIRONMENT