com.sagebrew.web
================
Must run `sudo apt-get install postfix` for email stuff to work correctly.


Don't need to do it right now but if we move over to having some views available
publicly might need to use something like:
`@authentication_classes((SessionAuthentication, BasicAuthentication))`
Rather than setting it globally in the settings for authentication.

### TextBlob/NLTK ###
```
pip install nltk
```
```
python manage.py shell
import nltk
nltk.download()
```
Then select download then hit enter until you see [ ]all come up and type in all
Do not need to include it in the settings.INSTALLED_APPS

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
