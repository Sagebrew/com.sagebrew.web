com.sagebrew.web
================
Must run `sudo apt-get install postfix` for email stuff to work correctly.


Don't need to do it right now but if we move over to having some views available
publicly might need to use something like:
`@authentication_classes((SessionAuthentication, BasicAuthentication))`
Rather than setting it globally in the settings for authentication.

### TextBlob/NLTK ###
'''
pip install nltk
'''
'''
python manage.py shell
import nltk
nltk.download()
'''
Then select download then hit enter until you see [ ]all come up and type in all
Do not need to include it in the settings.INSTALLED_APPS

### RabbitMQ ###
```
sudo rabbitmqctl delete_user guest
sudo rabbitmqctl add_user sagebrew this_is_the_sagebrew_password
sudo rabbitmqctl set_user_tags sagebrew administrator
sudo rabbitmqctl set_permissions sagebrew ".*" ".*" ".*"
```

### Neo4j ###
set neo4j db create file
`/etc/profile.d/neo.sh`
insert `export NEO4J_REST_URL=http://username:password@graphenedburl.com:port/db/data/`
then run `vagrant halt`
then `fab start_dev`

```
sudo -s
wget -O - http://debian.neo4j.org/neotechnology.gpg.key | apt-key add -
echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
apt-get update
apt-get install neo4j=1.9
cd /var/lib/neo4j/conf/
```

`sudo pico neo4j-server.properties` uncomment `org.neo4j.server.webserver.address=0.0.0.0`

`sudo pico /etc/nginx/nginx.conf`
replace the file with
```
include /etc/nginx/conf.d/base.nginxconf;
http{
    include mime.types;
    default_type application/octet-stream;
    access_log /var/log/nginx.access.log combined;
    sendfile on;
server {
    listen         80;
    return 301 https://$host$request_uri;
}


    include /etc/nginx/sites-enabled/*.nginxconf;
}
```

`sudo pico /etc/nginx/sites-available/sagebrew.nginxconf`


replace the contents with
```
upstream sagebrew {
    server unix:/home/apps/sagebrew/run/gunicorn.sock
    fail_timeout=0;
}

server {

    listen 443 ssl;
    ssl on;
    ssl_certificate /home/apps/certs/cert.pem;
    ssl_certificate_key /home/apps/certs/key.pem;
    ssl_protocols        SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers          HIGH:!aNULL:!MD5;

    access_log /tmp/sagebrewnginx.access.log;
    error_log /tmp/sagebrewnginx.error.log;

    client_max_body_size 4G;
    server_name 192.168.56.101;
    keepalive_timeout 5;

    location ~* ^/static/(.+)$ {
        root /home/apps/sagebrew;
        try_files /sagebrew/static/$1 /sb_registration/static/$1 /plebs/static/$1
                 /sb_comments/static/$1 /sb_posts/static/$1 /sb_relationships/static/$1 /sb_notifications/static/$1 /sb_questions/static/$1
                /sb_answers/static/$1 /sb_search/static/$1 /sb_tag/static/$1 @missing;
    }

    location /media {
        autoindex on;
        alias /home/apps/sagebrew/media/;
    }

    location / {
        # checks for static file, if not found proxy to app
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_read_timeout 1200;
        proxy_pass  http://0.0.0.0:8080;
    }

    error_page 500 502 503 504 /500.html;
    location = /500.html {
        root /home/apps/sagebrew/static/;
    }
}
```

```
ln -s /etc/nginx/sites-available/neoj.nginxconf /etc/nginx/sites-enabled/neoj.nginxconf
sudo service nginx reload
sudo service nginx restart
sudo service neo4j-service restart
```



### Fix for Nginx and Static File Collection in Dev ###

In the ngix config replace what we normally have as:
```
location /static {
        autoindex on;
        alias /home/apps/sagebrew/static/;
    }
```

with:
```
location ~* ^/static/(.+)$ {
        root /home/apps/sagebrew;
        try_files /sagebrew/static/$1 /sb_registration/static/$1 /plebs/static/$1
                 /sb_comments/static/$1 /sb_posts/static/$1 /sb_notifications/static/$1 @missing;
    }
```

Make sure to include all of the directories listed under STATICFILES_DIRS in the base.py file so that it grabs all of
them. This will check all of the folders in the list for static files and serve them up. This should work dynamically
as updates are made. This will need to be changed back in production for speed improvements but should alleviate the
issue of having to run `python manage.py collectstatic` whenever an update is made to the static files. It also enables
designers to still make modifications in an https environment meaning they get csrf and other django environment
benefits while designing templates.


## Docker Specifics ##
Ubuntu's default firewall (UFW: Uncomplicated Firewall) denies all forwarding traffic by default, which is needed by docker.

Enable forwarding with UFW:

Edit UFW configuration using the nano text editor.

sudo nano /etc/default/ufw
Scroll down and find the line beginning with DEFAULTFORWARDPOLICY.

Replace:

DEFAULT_FORWARD_POLICY="DROP"
With:

DEFAULT_FORWARD_POLICY="ACCEPT"
Press CTRL+X and approve with Y to save and close.

Finally, reload the UFW:

sudo ufw reload
