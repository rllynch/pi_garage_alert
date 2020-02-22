Pi Garage Alert
===============

Raspberry Pi Python script to email, tweet, or send an SMS if a garage door is left open.

![Screenshot of garage door SMS alert](http://www.richlynch.com/wp-content/uploads/2013/07/garage_door_sms.png)

Quick Start
---------------

Here is a heavily condensed quick start guide. New users are strongly encouraged to read the full documentation at http://www.richlynch.com/code/pi_garage_alert.

1. Equipment required
  1. Raspberry Pi model A or B
	1. 2GB or larger SD card for the RPi filesystem
	1. Magnetic sensor (e.g. http://www.smarthome.com/7455/Seco-Larm-SM-226L-Garage-Door-Contacts-for-Closed-Circuits/p.aspx)
	1. USB wifi adapter (if not using Ethernet)
	1. USB power supply for RPi
1. Connect one wire of the magnetic sensor to a GPIO pin on the RPi and the other to a ground pin on the RPi. It is a good idea to put a 1kohm resistor in series with the sensor to protect the RPi from damage if anything is misconfigured.
1. Raspberry Pi initial setup
	1. Follow the guide at http://elinux.org/RPi_Easy_SD_Card_Setup to write the Raspbian image to the SD card.
	1. Boot the RPi and at raspi-config, expand the filesystem, set the "pi" account password, set the hostname, and enable SSH.
	1. Reboot the Raspberry Pi
1. Edit /etc/wpa_supplicant/wpa_supplicant.conf and configure the RPi to connect to your wifi network.
1. Regenerate the ssh keys for security.
1. Update the packages with `sudo apt-get update && sudo apt-get upgrade`, then install the dependencies:<br>
sudo apt-get install git python3-dev python3-pip python3-rpi.gpio<br>
sudo pip3 install -r requirements.txt<br>
1. Optional email configuration
	1. Configure postfix to send mail using Google SMTP, or your ISP's SMTP server
1. Optional twitter configuration
	1. On https://dev.twitter.com/apps/new, create a new application
1. Optional twillio (SMS) configuration
	1. Sign up for a Twilio account at http://www.twilio.com.
1. Copy bin/pi_garage_alert.py to /usr/local/sbin
1. Copy etc/pi_garage_alert_config.py to /usr/local/etc. Edit this file and specify the garage doors you have and alerts you'd like.
1. Copy init.d/pi_garage_alert to /etc/init.d
1. Configure and start the service with<br>
sudo update-rc.d pi_garage_alert defaults<br>
sudo service pi_garage_alert start<br>
1. At this point, the Pi Garage Alert software should be running. You can view its log in /var/log/pi_garage_alert.log

Other Uses
---------------

The script will work with any sensor that can act like a switch. Some alternate uses include:

* Basement or washing machine leak sensors
* Window sensors
