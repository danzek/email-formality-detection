#!/usr/bin/env python
# -*- coding: utf_8 -*-
"""
Dan O'Day
Robert Hinh
Upasita Jain
Sangmi Shin
Penghao Wang

Purdue University
CNIT499 Natural Language Technologies
Time feature
"""
__author__ = "Robert Hinh"
__copyright__ = "Copyright 2014, Dan O'Day, Purdue University"
__credits__ = ["Dan O'Day", "Robert Hinh", "Upasita Jain", "Sangmi Shin", "Penghao Wang", "Julia Taylor"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Dan O'Day"
__email__ = "doday@purdue.edu"
__status__ = "Development"

#importing the libraries
import codecs,re,datetime,calendar,os,glob
from decimal import *

def day(email):
	fullDateCaptureLIST = email.time
	
	dayOfWeekRAW = fullDateCaptureLIST[1]
	#removing that comma
	#day of week
	day = dayOfWeekRAW[0:-1]

	return day

def time(email):
	fullDateCaptureLIST = email.time

	#day date
	time = str(fullDateCaptureLIST[5][0:5])
	
	hour = int(time[0:2])
	
	#half hour increments
	#for example - say it is 12.5, then the email was sent between 12:30 and 12:59:59
	#for example - say it is 12.0, then the email was sent between 12:0 and 12:29:59
	if (int(time[3:5]) < 30):
		halfHourIncrement = 0
	elif int(time[3:5]) > 30 and int(time[3:5]) < 60:
		halfHourIncrement = .5
	
	time = float(hour + halfHourIncrement)
	#making sure this will always be to the tenth place
	time = Decimal(time).quantize(Decimal('0.0'))
	
	#time extracted from the emails are sent in a 24-hour format
	return time

