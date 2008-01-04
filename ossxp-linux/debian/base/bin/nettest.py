#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2007 by the OpenSourceXpress co. ltd, Beijing, China.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Our website: 
# 	http://www.WorldHello.net
# 	http://www.OpenSourceXpress.com


'''Test network connections

Usage: %(program)s [options]

Options:

    -h|--help
            Print this message and exit.

    --host i:50:www.google.cn,i:50:www.sina.com.cn
            test www.google.cn and www.sina.com.cn, using i(cmp), with limit(50,80)

    -l|--loglevel debug|info|error
            Set loglevel

    -f|--logfile filename
            Save log to file

    -m|--mail user@domain.com
            Mail logs
    
    -q|--quiet
            Quiet mode

    -v|--verbose
            Verbose mode
'''

import sys, os, re, getopt, string
import logging,logging.handlers

program = sys.argv[0]
#logger = logging.getLogger('MyNetTest')

# Buffered SMTPLogger
class BufferingSMTPHandler(logging.handlers.BufferingHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject, capacity):
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.mailhost = mailhost
        self.mailport = None
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.setFormatter(logging.Formatter("%(levelname)s : %(asctime)-15s > %(message)s"))

    def flush(self):
        if len(self.buffer) > 0:
            try:
                import smtplib
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP(self.mailhost, port)
                msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (self.fromaddr, string.join(self.toaddrs, ","), self.subject)
                for record in self.buffer:
                    s = self.format(record)
                    print s
                    msg = msg + s + "\r\n"
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
                smtp.quit()
            except:
                self.handleError(None)  # no record failed in particular
            self.buffer = []


def usage(code=0, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__ % { 'program':program }
    if msg:
        print >> fd, msg
    return code


def network_test(hosts):
    if hosts is None:
        return 1

    if isinstance(hosts, (str, unicode)):
        hosts = hosts.split(',')

    testcase = []

    for host in hosts:
        case = {}
        element = host.split(':')
        if len(element) == 1:
            case['type'] = 'i'
            case['limit'] = '50'
            case['host'] = element[0]
        elif len(element) == 2:
            case['type'] = 'i'
            case['limit'] = element[0]
            case['host'] = element[1]
        else:
            case['type'] = element[0]
            case['limit'] = element[1]
            case['host'] = element[2]

        testcase.append(case)
        
    icmp_regex = re.compile(ur'^.* is alive \(([0-9\.]+) ms\)$', re.U)

    for case in testcase:
        host = case['host']
        type = case['type']
        limit = case['limit']

        logging.debug("NetTest for host:%s, type:%s, limt:%s" % (host,type,limit))

        if type == 'i': # icmp
            cmd = 'fping -e %s 2>&1' % host
            result_regex = icmp_regex
        else:
            cmd = "curl -L %s -m 5 -s 2>&1" % host
            result_regex = re.compile(limit, re.U)
        logging.debug("Cmd line: %s" % cmd)

        buff = os.popen(cmd).read().strip()
        if len(buff)>200:
            logging.debug("Buff: %s \r\n...\r\n%s " % (buff[0:70], buff[-70:]))
        else:
            logging.debug("Buff: %s " % buff)
        result = result_regex.search(buff)
        if result:
            logging.info("Host: %s match limit: %s" % (host, limit))

        try:
            if type == 'i': # icmp
                response_time = float(result.groups()[0])
                if response_time < float(limit):
                    logging.info("Test passed for %s" % host)
                else:
                    logging.error("Test FAILED for %s. Response time %.2f greater then limit:%s" % (host, response_time, limit))
            else:
                if result is None:
                    logging.error("Test FAILED for %s. No response, or response not match with %s" % (host, limit))
                    if len(buff)>200:
                        logging.error("Buff: %s \r\n...\r\n%s " % (buff[0:70], buff[-70:]))
                    else:
                        logging.error("Buff: %s " % buff)
                else:
                    logging.info("Test passed for %s" % host)
        except:
            logging.error("Unknown response for %s : %s" % (host, buff))

    logging.shutdown()


def main(argv=None):
    #opt_host = [ u"i:50:www.google.cn", u"i:50:www.sina.com.cn", u"h:Products/KnowledgeManagement:www.ossxp.com" ]
    opt_host = [ u"i:50:www.google.cn", u"i:50:www.sina.com.cn", u"h:Nielsen:www.sina.com.cn" ]
    opt_loglevel = None
    opt_logfile = None
    opt_mail = None
    opt_verbose = False
    loglevel=logging.DEBUG

    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt( 
            argv[1:], "hH:l:f:m:vq", 
            ["help", "verbose", "quiet", "host=", "loglevel=", "logfile=", "mail="])
    except getopt.error, msg:
        return usage(1, msg)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-H", "--host"):
            opt_host = arg
        elif opt in ("-l", "--loglevel"):
            opt_loglevel = arg.lower()
        elif opt in ("-f", "--logfile"):
            opt_logfile = arg
        elif opt in ("-m", "--mail"):
            opt_mail = arg
        elif opt in ("-v", "--verbose"):
            opt_verbose = True
        elif opt in ("-q", "--quiet"):
            opt_verbose = False
        else:
            return usage(1)

    if opt_verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.ERROR

    if opt_loglevel == 'critical':
        loglevel = logging.CRITICAL
    elif opt_loglevel == 'info':
        loglevel = logging.INFO
    elif opt_loglevel == 'warning':
        loglevel = logging.WARNING
    elif opt_loglevel == 'error':
        loglevel = logging.ERROR
    elif opt_loglevel is not None:
        loglevel = logging.DEBUG

    log_format = "%(levelname)s : %(asctime)-15s > %(message)s"
    log_options = {}
    log_options['format'] = log_format
    log_options['level'] = loglevel
        
    logging.basicConfig(**log_options)

    # log to file
    if isinstance(opt_logfile, (str,unicode)):
        logger_f = logging.FileHandler(opt_logfile)
        logger_f.setLevel(loglevel)
        logger_f.setFormatter(logging.Formatter(log_format))
        # add file_logger to root logger
        logging.getLogger('').addHandler(logger_f)

    # log to mail
    if isinstance(opt_mail, (str,unicode)):
        #logger_m = logging.handlers.SMTPHandler('localhost','root@foo.bar', opt_mail, 'NetTester')

        # using a buffered smtp logger
        logger_m = BufferingSMTPHandler('localhost','root@foo.bar', opt_mail, 'NetTester', 10)
        logger_m.setLevel(loglevel)
        logger_m.setFormatter(logging.Formatter(log_format))

        # add mail_logger to root logger
        logging.getLogger('').addHandler(logger_m)

    if opt_host is not None:
        return network_test(opt_host)
    else:
        print "Nothing to test!"
        return 1

   
if __name__ == "__main__":
    sys.exit(main())
