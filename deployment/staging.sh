#!/bin/sh

SHA1=$1
docker push sagebrew/sb_web:$SHA1
docker push sagebrew/sb_worker:$SHA1
docker push sagebrew/sys_util:$SHA1
EB_BUCKET=sagebrew-$CIRCLE_BRANCH
DOCKERRUN_FILE_WEB=$SHA1-staging_web.aws.json
DOCKERRUN_FILE_WORKER=$SHA1-staging_worker.aws.json
DOCKERRUN_WEB_ENVIRONMENT=/home/ubuntu/com.sagebrew.web/$SHA1-staging_web.json
DOCKERRUN_WORKER_ENVIRONMENT=/home/ubuntu/com.sagebrew.web/$SHA1-staging_worker.json
DOCKERRUN_FILE_SYS=$SHA1-staging_sys-util.aws.json

sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_worker/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.worker_template > $DOCKERRUN_FILE_WORKER
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_web/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_WEB
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sys_util/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_SYS


# TODO Make sure to set AWS_DEFAULT_REGION to us-east-1 https://pypi.python.org/pypi/awscli
# Also need to make sure to set permissions on dockercfg file so that all authenticated users
# can access it
# Make sure to add AWS creds to circle
aws s3 cp $DOCKERRUN_FILE_WEB s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_WEB
aws s3 cp $DOCKERRUN_FILE_WORKER s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_WORKER
aws s3 cp $DOCKERRUN_FILE_SYS s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_SYS

~/virtualenvs/venv-system/bin/python ~/sagebrew/deployment/deployment.py staging