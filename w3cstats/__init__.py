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
class LogStat(object):
    """Initialize statistics based on logs for 10 seconds

    :param str section: Section URI
    """
    def __init__(self, section):
        """Init method"""
        self.uri = section
        self.hits = 0
        self.status = {}
        self.host = {}
        self.total_size = 0
        self.min_size = 0
        self.max_size = 0

    def __str__(self):
        return("""{}: {} hits
  - total size: {}
  - total hits: {}\n  - hosts: {}
  - status: {}""".format(self.uri, self.hits, self.total_size,
                         self.hits, self.host, self. status))

    def add_hit(self, host, status, size):
        """Add a hit to statitics

        :param str host: Client host
        :param int status: HTTP status code
        :param float size: Size of the content
        """
        self.hits += 1

        self.total_size += size
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
