#!/bin/sh

SHA1=$1
docker push sagebrew/sb_web:$SHA1
docker push sagebrew/sb_worker:$SHA1
EB_BUCKET=sagebrew-$CIRCLE_BRANCH/$DOCKER_CONFIG_BUCKET
DOCKERRUN_FILE_WEB=$SHA1-master_Docker_web.aws.json
DOCKERRUN_FILE_WORKER=$SHA1-master_Docker_worker.aws.json
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_worker/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.worker_template > $DOCKERRUN_FILE_WORKER
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_web/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_WEB

aws s3 cp $DOCKERRUN_FILE_WEB s3://$EB_BUCKET/$DOCKERRUN_FILE_WEB

#/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb

aws elasticbeanstalk create-application-version --application-name production-web \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE_WEB

aws elasticbeanstalk update-environment --environment-name production-web-env \
    --version-label $SHA1




aws s3 cp $DOCKERRUN_FILE_WORKER s3://$EB_BUCKET/$DOCKERRUN_WORKER

#/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb

aws elasticbeanstalk create-application-version --application-name production-worker \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE_WORKER

aws elasticbeanstalk update-environment --environment-name production-worker-env \
    --version-label $SHA1