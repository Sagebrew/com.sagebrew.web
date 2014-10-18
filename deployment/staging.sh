#!/bin/sh

SHA1=$1
EB_BUCKET=$DOCKER_BUCKET
DOCKERRUN_FILE=$SHA1-Dockerrun.aws.json
sed "s/<TAG>/$SHA1/" < Dockerrun.aws.json.template > $DOCKERRUN_FILE

aws s3 cp $DOCKERRUN_FILE s3://$EB_BUCKET/$DOCKERRUN_FILE
/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb
aws elasticbeanstalk create-application-version --application-name staging \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE

aws elasticbeanstalk update-environment --environment-name staging-env \
    --version-label $SHA1