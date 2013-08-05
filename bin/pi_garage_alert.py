#!/usr/bin/python2.7
""" Pi Garage Alert

Author: Richard L. Lynch <rich@richlynch.com>

Description: Emails, tweets, or sends an SMS if a garage door is left open
too long.

Learn more at http://www.richlynch.com/code/pi_garage_alert
"""

##############################################################################
#
# The MIT License (MIT)
# 
# Copyright (c) 2013 Richard L. Lynch <rich@richlynch.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
##############################################################################

import RPi.GPIO as GPIO
import time
import subprocess
import re
import sys
import tweepy
import smtplib
from email.mime.text import MIMEText

from time import strftime
from datetime import timedelta
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException

sys.path.append('/usr/local/etc')
import pi_garage_alert_config as cfg


##############################################################################
# Twilio support
##############################################################################

twilio_client = None

def twilio_send_sms(recipient, msg):
    """Sends SMS message to specified phone number using Twilio.

    Args:
        recipient: Phone number to send SMS to.
        msg: Message to send. Long messages will automatically be truncated.
    """
    global twilio_client

    # User may not have configured twilio - don't initialize it until it's
    # first used
    if twilio_client == None:
        status("Initializing Twilio")
        
        if cfg.TWILIO_ACCOUNT == '' or cfg.TWILIO_TOKEN == '':
            status("Twilio account or token not specified - unable to send SMS!")
        else:
            twilio_client = TwilioRestClient(cfg.TWILIO_ACCOUNT, cfg.TWILIO_TOKEN)

    if twilio_client != None:
        status("Sending SMS to %s: %s" % (recipient, msg))
        try:
            twilio_client.sms.messages.create(
                to = recipient, 
                from_ = cfg.TWILIO_PHONE_NUMBER, 
                body = truncate(msg, 140))
        except TwilioRestException, ex:
            status("Unable to send SMS: %s" % (ex))

##############################################################################
# Twitter support
##############################################################################

twitter_api = None

def twitter_dm(user, msg):
    """Send direct message to specified Twitter user.

    Args:
        user: User to send DM to.
        msg: Message to send. Long messages will automatically be truncated.
    """
    global twitter_api

    # User may not have configured twitter - don't initialize it until it's
    # first used
    if twitter_api == None:
        status("Initializing Twitter")

        if cfg.TWITTER_CONSUMER_KEY == '' or cfg.TWITTER_CONSUMER_SECRET == '':
            status("Twitter consumer key/secret not specified - unable to Tweet!")
        elif cfg.TWITTER_ACCESS_KEY == '' or cfg.TWITTER_ACCESS_SECRET == '':
            status("Twitter access key/secret not specified - unable to Tweet!")
        else:
            auth = tweepy.OAuthHandler(cfg.TWITTER_CONSUMER_KEY, cfg.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(cfg.TWITTER_ACCESS_KEY, cfg.TWITTER_ACCESS_SECRET)
            twitter_api = tweepy.API(auth)

    if twitter_api != None:
        # Twitter doesn't like the same msg sent over and over, so add a timestamp
        msg = strftime("%Y-%m-%d %H:%M:%S: ") + msg
        
        status("Sending twitter DM to %s: %s" % (user, msg))
        try:
            twitter_api.send_direct_message(user = user, text = truncate(msg, 140))
        except tweepy.error.TweepError, ex:
            status("Unable to send Tweet: %s" % (ex))

##############################################################################
# Email support
##############################################################################

def send_email(recipient, subject, msg):
    """Sends an email to the specified email address.

    Args:
        recipient: Email address to send to.
        subject: Email subject.
        msg: Body of email to send.
    """
    status("Sending email to %s: subject = \"%s\", message = \"%s\"" % (recipient, subject, msg))

    msg = MIMEText(msg)
    msg['Subject'] = subject
    msg['To'] = recipient
    msg['From'] = cfg.EMAIL_FROM

    mail = smtplib.SMTP(cfg.SMTP_SERVER, cfg.SMTP_PORT)
    mail.sendmail(cfg.EMAIL_FROM, recipient, msg.as_string())
    mail.quit()

##############################################################################
# Sensor support
##############################################################################

def get_garage_door_state(pin):
    """Returns the state of the garage door on the specified pin as a string

    Args:
        pin: GPIO pin number.
    """
    if GPIO.input(pin):
        state = 'open'
    else:
        state = 'closed'

    return state

def get_uptime():
    """Returns the uptime of the RPi as a string
    """
    with open('/proc/uptime', 'r') as uptime_file:
        uptime_seconds = int(float(uptime_file.readline().split()[0]))
        uptime_string = str(timedelta(seconds = uptime_seconds))
    return uptime_string

def get_gpu_temp():
    """Return the GPU temperature as a Celsius float
    """
    cmd = ['vcgencmd', 'measure_temp']

    measure_temp_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, errors = measure_temp_proc.communicate()

    gpu_temp = 'unknown'
    gpu_search = re.search('([0-9.]+)', output)

    if gpu_search:
        gpu_temp = gpu_search.group(1)

    return float(gpu_temp)

def get_cpu_temp():
    """Return the CPU temperature as a Celsius float
    """
    cpu_temp = 'unknown'
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as temp_file:
        cpu_temp = float(temp_file.read()) / 1000.0

    return cpu_temp

def rpi_status():
    """Return string summarizing RPi status
    """
    return ("CPU temp: %.1f, GPU temp: %.1f, Uptime: %s" % (get_gpu_temp(), get_cpu_temp(), get_uptime()))

##############################################################################
# Logging and alerts
##############################################################################
log_file_handle = None

def status(msg):
    """Log status message to LOG_FILENAME.

    Args:
        msg: message to log.
    """
    global log_file_handle

    line = strftime("%Y-%m-%d %H:%M:%S: ") + msg
    print line

    if log_file_handle == None:
        log_file_handle = open(cfg.LOG_FILENAME, 'a')

    log_file_handle.write(line + "\n")
    log_file_handle.flush()

def send_alerts(recipients, subject, msg):
    """Send subject and msg to specified recipients

    Args:
        recipients: An array of strings of the form type:address
        subject: Subject of the alert
        msg: Body of the alert
    """
    for recipient in recipients:
        if recipient[:6] == 'email:':
            send_email(recipient[6:], subject, msg)
        elif recipient[:11] == 'twitter_dm:':
            twitter_dm(recipient[11:], msg)
        elif recipient[:4] == 'sms:':
            twilio_send_sms(recipient[4:], msg)
        else:
            status("Unrecognized recipient type: %s" % (recipient))

##############################################################################
# Misc support
##############################################################################

def truncate(input_str, length):
    """Truncate string to specified length

    Args:
        input_str: String to truncate
        length: Maximum length of output string
    """
    if len(input_str) < (length - 3):
        return input_str

    return input_str[:(length - 3)] + '...'

##############################################################################
# Main functionality
##############################################################################
def main():
    """Main functionality
    """

    # Banner
    status("==========================================================")
    status("Pi Garage Alert starting")

    # Use Raspberry Pi board pin numbers
    status("Configuring global settings")
    GPIO.setmode(GPIO.BOARD)

    # Configure the sensor pins as inputs with pull up resistors
    for door in cfg.GARAGE_DOORS:
        status("Configuring pin %d for \"%s\"" % (door['pin'], door['name']))
        GPIO.setup(door['pin'], GPIO.IN, pull_up_down = GPIO.PUD_UP)

    # Last state of each garage door
    door_states = dict()

    # time.time() of the last time the garage door changed state
    time_of_last_state_change = dict()

    # Index of the next alert to send for each garage door
    alert_states = dict()

    # Read initial states
    for door in cfg.GARAGE_DOORS:
        name = door['name']
        state = get_garage_door_state(door['pin'])

        door_states[name]                = state
        time_of_last_state_change[name]  = time.time()
        alert_states[name]               = 0

        status("Initial state of \"%s\" is %s" % (name, state))

    status_report_countdown = 5
    while (1):
        for door in cfg.GARAGE_DOORS:
            name = door['name']
            state = get_garage_door_state(door['pin'])
            time_in_state = time.time() - time_of_last_state_change[name]

            # Check if the door has changed state
            if door_states[name] != state:
                door_states[name] = state
                time_of_last_state_change[name] = time.time()
                status("State of \"%s\" changed to %s after %.0f sec" % (name, state, time_in_state))

                # Reset alert when door changes state
                if alert_states[name] > 0:
                    # Use the recipients of the last alert
                    recipients = door['alerts'][alert_states[name] - 1]['recipients']
                    send_alerts(recipients, name, "%s is now %s" % (name, state))
                    alert_states[name] = 0

                # Reset time_in_state
                time_in_state = 0

            # See if there are more alerts
            if len(door['alerts']) > alert_states[name]:
                # Get info about alert
                alert = door['alerts'][alert_states[name]]

                # Has the time elapsed and is this the state to trigger the alert?
                if time_in_state > alert['time'] and state == alert['state']:
                    send_alerts(alert['recipients'], name, "%s has been %s for %d seconds!" % (name, state, time_in_state))
                    alert_states[name] += 1

        # Periodically log the status for debug and ensuring RPi doesn't get too hot
        status_report_countdown -= 1
        if status_report_countdown <= 0:
            status_msg = rpi_status()

            for name in door_states:
                status_msg += ", %s: %s/%d/%d" % (name, door_states[name], alert_states[name], (time.time() - time_of_last_state_change[name]))

            status(status_msg)

            status_report_countdown = 600

        # Poll every 1 second
        time.sleep(1)
    
    # Will never actually get here unless while(1) condition changed
    GPIO.cleanup() 

if __name__ == "__main__":
    # Ensure GPIO.cleanup() is called on ctrl-c termination
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()

