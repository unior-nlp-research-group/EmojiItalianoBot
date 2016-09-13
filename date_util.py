# -*- coding: utf-8 -*-

from datetime import datetime as datetime
from pytz.gae import pytz

UTC_ZONE = pytz.timezone('UTC')
CET_ZONE = pytz.timezone('CET')

def now():
    #return datetime.now()
    utc = datetime.now()
    utc = utc.replace(tzinfo=UTC_ZONE)
    return utc.astimezone(CET_ZONE)

def timeString(dt=now(), ms=False):
    if ms:
        return dt.strftime('%H:%M:%S.%f')[:-3]
    return dt.strftime('%H:%M:%S')

def dateString(dt=now()):
    return dt.strftime('%d/%m/%y')

def dateTimeString(dt=now()):
    return dt.strftime('%d/%m/%y %H:%M:%S')


