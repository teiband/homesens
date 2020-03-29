# HomeSens
The framework consists of two modules:
* bme280
    * sensor data acquisition with bme280 sensor chip
    * repository
* homesens
    * web application based on Flask
    * this repository

## BME280: Sensor Data Acquisition
Sensor data is acquired periodically based on a linux cron-job. The acquired data is written into a **sqlite3** database. The cron-job assures that sensor data is always captured independent of the functionality of the web application.

### Cron configuration
This config (edit by `crontab -e`) calls the sensor script every 30 minutes:

```
*/30 * * * * /home/pi/workspace/bme280/send_mail_on_error.bash
```

### Sensor Configuration
TODO

## The Web Application
The project based on python2.7 is stored in `/home/pi/workspace/homesens`. It is configured as Flask app with the main script in
`homesens/homesens.py`


### Startup
Can be started manually with the script in
`./homesens` / `start_flask_public.sh` or `start_with_python2.7_public.sh`

## Webserver
The webserver is an Apache2 server. It can be controlled with
```
sudo service apache2 start/stop/restart
```
### Configuration

## WSGI Configuration
WSGI [(Web Server Gateway Interface)](https://en.m.wikipedia.org/wiki/Web_Server_Gateway_Interface) builds the connection between python application and web server.
The config file of the WSGI application need to be stored under `/etc/apache2/sites-enabled/homesens.conf`

```apache
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
```

## Requirements

```
apache2
flask
```
