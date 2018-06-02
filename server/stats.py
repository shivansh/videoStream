#!/usr/bin/env python

import sys

A = "Sending index"
B = "Populating index"
C = "Covered up, waiting for writer"
D = "Payloads delivered"

f = open(sys.argv[1], 'r')

num_thred_switches = 0
num_lags = 0
curr_read = None
prev_read = None

for line in f:
    if A in line:
        prev_read = curr_read
        curr_read = A
    elif B in line:
        prev_read = curr_read
        curr_read = B
    if C in line:
        num_lags += 1

    if (curr_read == A and prev_read == B) or (curr_read == B and
                                               prev_read == A):
        num_thred_switches += 1
    if D in line:
        print line,

print "Number of Thread switches", num_thred_switches
print "Number of lags occured", num_lags
