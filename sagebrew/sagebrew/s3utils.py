from storages.backends.s3boto import S3BotoStorage


MediaRootS3BotoStorage  = lambda: S3BotoStorage(location='media')
StaticRootS3BotoStorage  = lambda: S3BotoStorage(location='static')
