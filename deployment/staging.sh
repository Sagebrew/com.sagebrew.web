#!/bin/sh

SHA1=$1
docker push sagebrew/sb_web:$SHA1
docker push sagebrew/sb_worker:$SHA1
docker push sagebrew/sys_util:$SHA1
EB_BUCKET=sagebrew-$CIRCLE_BRANCH
DOCKERRUN_FILE_WEB=$SHA1-staging_web.aws.json
WEB_ZIP=$SHA1-staging_web.zip
DOCKERRUN_FILE_WORKER=$SHA1-staging_worker.aws.json
WORKER_ZIP=$SHA1-staging_worker.zip
DOCKERRUN_WORKER_ENVIRONMENT=/home/ubuntu/com.sagebrew.web/$SHA1-staging_worker.json
DOCKERRUN_FILE_SYS=$SHA1-staging_sys-util.aws.json

sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sys_util/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_SYS
aws s3 cp $DOCKERRUN_FILE_SYS s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_SYS

cd /home/ubuntu/com.sagebrew.web/aws_bundle/
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_web/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_WEB
zip -r $WEB_ZIP .
rm $DOCKERRUN_FILE_WEB
aws s3 cp $WEB_ZIP s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$WEB_ZIP
rm $WEB_ZIP

sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_worker/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.worker_template > $DOCKERRUN_FILE_WORKER
zip -r $WORKER_ZIP .
aws s3 cp $WORKER_ZIP s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$WORKER_ZIP
rm $DOCKERRUN_FILE_WORKER

~/virtualenvs/venv-system/bin/python ~/com.sagebrew.web/deployment/deployment.py staging