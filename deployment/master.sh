#!/bin/sh

SHA1=$1
docker push sagebrew/sb_web:$SHA1
docker push sagebrew/sb_worker:$SHA1
docker push sagebrew/sys_util:$SHA1
EB_BUCKET=sagebrew-$CIRCLE_BRANCH
DOCKERRUN_FILE_WEB=$SHA1-master_web.aws.json
WEB_ZIP=$SHA1-master_web.zip
DOCKERRUN_FILE_WORKER=$SHA1-master_worker.aws.json
WORKER_ZIP=$SHA1-master_worker.zip
DOCKERRUN_WORKER_ENVIRONMENT=/home/ubuntu/com.sagebrew.web/$SHA1-master_worker.json
DOCKERRUN_FILE_SYS=$SHA1-master_sys-util.aws.json

sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_worker/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.worker_template > $DOCKERRUN_FILE_WORKER
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_web/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_WEB
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sys_util/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_SYS
zip $WEB_ZIP $DOCKERRUN_FILE_WEB /home/ubuntu/com.sagebrew.web/.ebextensions
zip $WORKER_ZIP $DOCKERRUN_FILE_WEB /home/ubuntu/com.sagebrew.web/.ebextensions

# Make sure to set AWS_DEFAULT_REGION to us-east-1 https://pypi.python.org/pypi/awscli
# Also need to make sure to set permissions on dockercfg file so that all authenticated users
# can access it
# Make sure to add AWS creds to circle
aws s3 cp $WEB_ZIP s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$WEB_ZIP
aws s3 cp $WORKER_ZIP s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$WORKER_ZIP
aws s3 cp $DOCKERRUN_FILE_SYS s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_SYS

~/virtualenvs/venv-system/bin/python ~/com.sagebrew.web/deployment/deployment.py master