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

#if I have time, I'll add in the time zones method to standardize time

def day(email):
	fullDateCaptureSTR = str(email.date)
	fullDateCaptureLIST = fullDateCaptureSTR.split(' ')

	dayOfWeekRAW = fullDateCaptureLIST[1]
	#removing that comma
	#day of week
	day = dayOfWeekRAW[0:-1]

	#just using an if-statement. I assume email.date is a string object anyways and not a date object
	#but in theory, if email.date is a date object, then use this:
	#.weekday() - 0 is Monday
	if day == 'Sun':
		day = 0
	elif day == 'Mon':
		day = 1
	elif day == 'Tue':
		day = 2
	elif day == 'Wed':
		day = 3
	elif day == 'Thu':
		day = 4
	elif day == 'Fri':
		day = 5
	elif day == 'Sat':
		day = 6

	print(day)

def time(email):
	fullDateCaptureSTR = str(email.date)
	fullDateCaptureLIST = fullDateCaptureSTR.split(' ')
	
	#day date
	time = str(fullDateCaptureLIST[5][0:5])
	
	hour = int(time[0:2])
	
	#4 hour increments
	#0,4,8,12,16,20
	if hour >= 0 and hour < 4:
		range = 0
	elif hour >= 4 and hour < 8:
		range = 1
	elif hour >= 8 and hour < 12:
		range = 2
	elif hour >= 12 and hour < 16:
		range = 3
	elif hour >= 16 and hour < 20:
		range = 4
	elif hour >= 20 and hour < 0:
		range = 5

	#time extracted from the emails are sent in a 24-hour format
	return range

