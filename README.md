## Automated Test Client ##
Need to ensure that camera is positioned so that when VLC is opened it automatically corrects its focus. This can be accomplished by getting the right amount of light and centering the camera correctly.

Also to activate webcam on VM, must spawn up GUI, click the devices dropdown, select webcams, and then select the webcam you would like to use. Just using the usb filter does not seem to work.

Webcam also requires VirtualBox extension pack


### Notes on Comprobe ###
Change IP address in FTSAutoServer.exe.config which is located in C:\Pro- gram Files (x86)\Frontline Test System II\Frontline ComProbe Protocol Analysis System 12.9.478.550\Executables\Core

Run as Administrator


### Notes on Memcache ###
Need to install `memcached`, `libmemcached-tools`, `libmemcached-dev`, and  to install `pylibmc`

### Redis Notes ###
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
sudo cp utils/redis_init_script /etc/init.d/redis_6379
sudo vi /etc/init.d/redis_6379
sudo cp redis.conf /etc/redis/6379.conf
sudo mkdir /var/redis/6379
cd /etc/redis/
ls
sudo pico 6379.conf 
sudo update-rc.d redis_6379 defaults
sudo service redis_6379 start
redis-cli

### Notes on Webcam ###
When hooking up the webcam ensure that you open it with VLC and position it in a way that will consistently cause it to auto-focus.

You must open the webcam with VLC prior to booting up the VM otherwise the webcam will not appear as an option under the devices. As of this writting this only applies to Virtualbox but has not been tested on VMWare or Parrallels.

Also if you experience issues with the webcam hanging in the VM then ensure your VLC app isn't attempting to utilize the camera. Issues were seen in version 2.1.x on OSX but 2.0.x appears to have less issues with running into errors when turning off its access to logitech webcams. If you are forced to Force Close the VLC app it is probably tying up the link in the background and may cause intermittent issues.
