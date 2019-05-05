#
#    Application dependencies management (pydeps)
#
#    Copyright (C) 2017 Cyrielle Camanes (sylicia) <cyrielle.camanes@gmail.com>
#
#    This file is part of pydeps
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, see <http://www.gnu.org/licenses/>.


import logging
import os
import re
from datetime import datetime, timedelta
from .exceptions import DependencyError

logger = logging.getLogger(__name__)

HOST = r'^(?P<host>.*?)'
SEP = r'\s'
IDENTITY = r'\S+'
USER = r'\S+'
TIME = r'\[(?P<time>.*?)\]'
SECTION = r'\"\S+\s(?P<section>/[^/\s]*).*?\"'

STATUS = r'(?P<status>\d{3})'
SIZE = r'(?P<size>\S+)'

REGEX = HOST+SEP+IDENTITY+SEP+USER+SEP+TIME+SEP+SECTION+SEP+STATUS+SEP+SIZE+SEP
parser = re.compile(REGEX)

W3C_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

#
#   Functions
#

def to_period_stats(time_string):
    """Convert a date into a timestamp related a period.
    Periods are defined every 10 seconds from 0.

    :param str time_string: Time in W3C format
    :return: The related period as datetime
    """
    date_time = datetime.strptime(time_string, W3C_TIME_FORMAT)
    to_sub = int(str(int(date_time.timestamp()))[-1])
    return (date_time - timedelta(seconds=to_sub))

def to_period_alert(time_string):
    """Convert a date into a timestamp related a period.
    Periods are defined every 10 seconds from 0.

    :param str time_string: Time in W3C format
    :return: The related period as datetime
    """
    sec_to_sub = 0
    min_to_sub = 0

    if time_string.second != 0:
        sec_to_sub = time_string.second
    if time_string.minute%2 != 0:
        min_to_sub = 1

    date_time = time_string - timedelta(minutes=min_to_sub, seconds=sec_to_sub)
    logger.info("Period for alerting: {}".format(date_time))
    return(date_time)


def parse_log(log_line):
    """Parse a log line and extract interesting sections

    :param str log_line: W3C line to parse
    :return: Dict with useful fields
    """
    logger.debug("Line: {}".format(log_line[0:-1]))
    match = parser.search(log_line)
    if not match:
        if len(log_line) > 0:
            logger.warning("Invalid Line: {}".format(log_line[0:-1]))
            return(None)
    result = {
            'host': match.group('host'),
            'section': match.group('section') ,
            'status': int(match.group('status')) ,
            'size': float(match.group('size')),
            'time_period': to_period_stats(match.group('time'))
    }
    logger.debug(result)
    return (result)

def register_log(sections, log_parsed):
    """Register the log parsed

    :param dict sections: Sections list
    :param dict log_parsed: Log parsed
    """
    logger.info("Register: {}".format(log_parsed))
    if log_parsed['section'] not in sections:
        sections[log_parsed['section']] = LogStat(log_parsed['section'])
    sections[log_parsed['section']].add_hit(
        log_parsed['host'],
        log_parsed['status'] ,
        log_parsed['size']
    )

#
#   Class
#
class Alerts(object):
    """Statistics based on logs and alerting

    :param str section: Section URI
    """
    def __init__(self, start_time, date_time):
        """Init method"""
        self.start_time = start_time
        self.date_time = date_time
        self.end_time = None
        self.duration = None
        self.average = None
        self.sections = {}
        self.hits = 0
        self.in_alert = False

    def add_section(self, section):
        """Add a hit to statitics

        :param LogStat section: Section statistics
        """
        self.hits += section.hits
        if section.uri not in self.sections:
            self.sections[section.uri] = section.hits
        else:
            self.sections[section.uri] += section.hits
        logger.debug("Update alert {} : {}".format(self.date_time, self.hits))

    def close(self, limit, curr_time):
        logger.info("Close period: {}".format(self.date_time))
        self.end_time = curr_time
        self.duration = (self.end_time-self.start_time).total_seconds()
        self.average = self.hits/self.duration
        if self.average > limit:
            print("ALERT at {} traffic average is high ({:.0f} hits/second)".format(self.date_time, self.average))
            self.in_alert = True
        else:
            logger.info("No alert at {} traffic average is high ({:.0f} hits/second)".format(self.date_time, self.average))
        return(self.in_alert)

class LogStat(object):
    """Statistics based on logs for 10 seconds

    :param str section: Section URI
    """
    def __init__(self, section):
        """Init method"""
        self.uri = section
        self.hits = 0
        self.status = {}
        self.host = {}
        self.size = 0
        self.min_size = 0
        self.max_size = 0

    def __str__(self):
        return("""{}: {} hits
  - total size: {}
  - total hits: {}\n  - hosts: {}
  - status: {}""".format(self.uri, self.hits, self.size,
                         self.hits, self.host, self. status))

    def add_hit(self, host, status, size):
        """Add a hit to statitics

        :param str host: Client host
        :param int status: HTTP status code
        :param float size: Size of the content
        """
        self.hits += 1

        self.size += size
        if size < self.min_size:
            self.min_size = size
        if size > self.max_size:
            self.max_size = size

        if status not in self.status:
            self.status[status] = 1
        else:
            self.status[status] += 1

        if host not in self.host:
            self.host[host] = 1
        else:
            self.host[host] += 1

    @property
    def error_rate(self):
        """Give the percentage of errors from 400

        :return: Percentage
        """
        count_errors = 0

        for status in self.status:
            if status >= 400:
                count_errors += self.status[status]
        return(count_errors * 100 / self.hits)
