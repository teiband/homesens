# homesens

## Python Project
The project based on python2.7 is stored in ˋ/home/pi/workspace/homesensˋ. It is configured as Flask app with the main script in
ˋhomesens/homesens.pyˋ

### Startup
Can be started manually with the script in
ˋ./homesensˋ / ˋstart_flask_public.shˋ or ˋstart_with_python2.7_public.shˋ

## Webserver
The webserver is an Apache2 server. It can be controlled with
'''
sudo service apache2 start/stop/restart
'''
### Configuration

## WSGI Configuration
WSGI [(Web Server Gateway Interface)](https://en.m.wikipedia.org/wiki/Web_Server_Gateway_Interface) builds the connection between python application and web server.
The config file of the WSGI application need to be stored under ˋ/etc/apache2/sites-enabled/homesens.confˋ
'''
<virtualhost *:80>
        ServerName homesens

        WSGIDaemonProcess homesens user=www-data group=www-data threads=5 home=/home/pi/workspace/homesens/ python-path=:/home/.pi/.local/lib/python2.7/site-packages
        #WSGIPythonPath :/home/pi/.local/lib/python2.7/site-packages
        WSGIScriptAlias / /var/www/homesens/homesens.wsgi

        <directory /var/www/homesens>
                WSGIProcessGroup homesens
                WSGIApplicationGroup %{GLOBAL}
                WSGIScriptReloading On
                Order deny,allow
                Allow from all
        </directory>

        # TE allow access to generated images
        <Directory /home/pi/workspace/homesens/homesens/static/images>
                <IfVersion < 2.4>
                    Order allow,deny
                    Allow from all
                </IfVersion>
                <IfVersion >= 2.4>
                    Require all granted
                </IfVersion>
        </Directory>
</virtualhost>
'''

## Requirements
'''
apache2
flask
'''
