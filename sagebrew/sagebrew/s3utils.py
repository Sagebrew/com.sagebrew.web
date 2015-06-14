from os import environ
from storages.backends.s3boto import S3BotoStorage


class SBS3BotoStorage(S3BotoStorage):
    def url(self, name):
        name = self._normalize_name(self._clean_name(name))
        if self.custom_domain:
            return "%s//%s/%s?v=%s" % (self.url_protocol,
                                       self.custom_domain, name,
                                       environ.get("SHA1", ""))
        return self.connection.generate_url(self.querystring_expire,
            method='GET', bucket=self.bucket.name, key=self._encode_name(name),
            query_auth=self.querystring_auth, force_http=not self.secure_urls)


MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')
StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')
