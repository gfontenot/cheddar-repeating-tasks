#!/usr/bin/python
#
# wwdc.py
#
# This script checks the Apple WWDC web page to see if the upcoming
# conference has been announced. The conference year to check is passed
# in on the command line. The script checks for the year in the <title>
# tag for the web page and for any occurance of WWDC [year]. If either
# is found then the script assumes the conference has been announced.
#
# To avoid a flood of emails, the script will broadcast the announcement
# only once. After the email is sent out the first time, the file 
# wwdc-annc-sent.txt is created in the output directory. If this file exists
# then additional emails are not sent.
#
# Example:
# ./wwdc.py -y 2012 -f from@email.com -t to@email.com -s mail.server.com -p 587 -P password
#
# cron example (checks site every 2 minutes):
# */2 * * * * /usr/bin/python /home/me/wwdc.py -y 2012 -f from@email.com -t to@email.com -s mail.server.com -p 587 -P password
#
# Copyright 2012 Kirby Turner
#
# Version 1.0
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import getopt
import urllib
import re
import smtplib
import socket
import os

class Options:
    def __getattr__(self, attrname):
        if attrname == 'year':
            return year
        elif attrname == 'toAddress':
            return toAddress
        elif attrname == 'fromAddress':
            return fromAddress
        elif attrname == 'smtpServer':
            return smtpServer
        elif attrname == 'smtpPort':
            return smtpPort
        elif attrname == 'password':
            return password
        elif attrname == 'outputDirectory':
            return outputDirectory
        else:
            raise AttributeError, attrname


def fetchHTML(url):
    f = urllib.urlopen(url)
    html = f.read()
    f.close()
    return html

def announcementSent(options):
    sent = False
    try:
        f = open(os.path.join(options.outputDirectory, 'wwdc-annc-sent.txt'))
        f.close()
        sent = True
    except IOError, e:
        sent = False
    return sent

def emailAnnouncement(options):
    if announcementSent(options):
        print 'Annoucement already sent.'
        return
    
    msg = """From: %s
To: %s
Reply-To: %s
Subject: WWDC %s Announcement

Buy your ticket now!

http://developer.apple.com/wwdc
"""%(options.fromAddress, options.toAddress, options.fromAddress, options.year)

    # # Use toaddr as the from address on the send mail call.
    # # This will ensure no greylisting problems with user
    # # email addresses.
    server = smtplib.SMTP(options.smtpServer, options.smtpPort)
    # Login to the mail server
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(options.fromAddress, options.password)
    server.sendmail(options.fromAddress, options.toAddress, msg)
    server.quit()
    
    f = open(os.path.join(options.outputDirectory, 'wwdc-annc-sent.txt'), 'w')
    try:
        f.write('WWDC annoucement sent.')
    finally:
        f.close()

    return 

def broadcastAnnoucement(options):
    print '====> WWDC %s has been announced! <====' % options.year
    if (len(options.toAddress) > 0):
        emailAnnouncement(options)
    return

def checkWebsite(options):
    html = fetchHTML('https://developer.apple.com/wwdc/')
    
    itsOn = False
    match = re.search('<title>(.*?)</title>', html)
    title = match.group(1)
    itsOn = options.year in title
    if (itsOn):
        broadcastAnnoucement(options)
    else:
        stringToMatch = 'WWDC %s' % options.year
        itsOn = stringToMatch in html
        if (itsOn):
            broadcastAnnoucement(options)
        else:
            print 'No WWDC %s announcement yet' % options.year

def usage():
    print '''usage: %s [options]
Options and arguments:
-h      : print this help message and exit (also --help)
-y nnnn : year to check (also --year)
-f email@domain.com : send from email address (also --from)
-t email@domain.com : send to email address (also --to)
-s name       : smtp server name (also --server)
-p portnumber : smtp port number (also --port)
-P password   : mail server password (also --password)
-o directory  : output directory (also --output)

''' % sys.argv[0]


def processCmdArgs():
    options = None
    try: 
        opts, args = getopt.getopt(sys.argv[1:], 'hy:f:t:s:p:P:o:', ['help', 'year=', 'from=', 'to=', 'server=', 'port=', 'password=', 'output='])
    except getopt.GetoptError, err:
        #print help information and exit
        print str(err)  # will print something like "option -x not recongized"
        usage()
        return None
        
    if len(opts) == 0:
        usage()
    else :
        options = Options()
        options.outputDirectory = ''
        options.toAddress = ''
        for o, a in opts:
            if o in ('-h', '--help'):
                usage()
                return None
            elif o in ('-y', '--year'):
                options.year = a
            elif o in ('-f', '--from'):
                options.fromAddress = a
            elif o in ('-t', '--to'):
                options.toAddress = a
            elif o in ('-s', '--server'):
                options.smtpServer = a
            elif o in ('-p', '--port'):
                options.smtpPort = a
            elif o in ('-P', '--password'):
                options.password = a
            elif o in ('-o', '--output'):
                options.outputDirectory = a
            else:
                assert False, 'unhandled option'
    
    return options


def main():
    options = processCmdArgs()
    if options == None:    # Will exit if usgae requested or invalid argument found.
      return 1

    checkWebsite(options)

if __name__ == '__main__':
  sys.exit(main())
 
