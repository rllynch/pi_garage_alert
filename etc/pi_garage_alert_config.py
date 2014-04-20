#!/usr/bin/python2.7

##############################################################################
# Global settings
##############################################################################

# Describes all the garage doors being monitored
GARAGE_DOORS = [
#    {
#        'pin': 16,
#        'name': "Garage Door 1",
#        'alerts': [
#            {
#                'state': 'open',
#                'time': 120,
#                'recipients': [ 'sms:+11112223333', 'sms:+14445556666' ]
#            },
#            {
#                'state': 'open',
#                'time': 600,
#                'recipients': [ 'sms:+11112223333', 'sms:+14445556666' ]
#            }
#        ]
#    },

    {
        'pin': 15,
        'name': "Example Garage Door",
        'alerts': [
#            {
#                'state': 'open',
#                'time': 120,
#                'recipients': [ 'sms:+11112223333', 'email:someone@example.com', 'twitter_dm:twitter_user', 'tweet' ]
#            },
#            {
#                'state': 'open',
#                'time': 600,
#                'recipients': [ 'sms:+11112223333', 'email:someone@example.com', 'twitter_dm:twitter_user', 'tweet' ]
#            }
        ]
    }
]

# All messages will be logged to stdout and this file
LOG_FILENAME = "/var/log/pi_garage_alert.log"

##############################################################################
# Email settings
##############################################################################

SMTP_SERVER = 'localhost'
SMTP_PORT = 25
EMAIL_FROM = 'Garage Door <user@example.com>'

##############################################################################
# Twitter settings
##############################################################################

# Follow the instructions on http://talkfast.org/2010/05/31/twitter-from-the-command-line-in-python-using-oauth/
# to obtain the necessary keys

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_KEY = ''
TWITTER_ACCESS_SECRET = ''

##############################################################################
# Twilio settings
##############################################################################

# Sign up for a Twilio account at https://www.twilio.com/
# then these will be listed at the top of your Twilio dashboard 

TWILIO_ACCOUNT = ''
TWILIO_TOKEN = ''

# SMS will be sent from this phone number
TWILIO_PHONE_NUMBER = '+11234567890'
