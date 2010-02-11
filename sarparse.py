#!/usr/bin/python
import os
from subprocess import *


os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin'


class Paging:
    def __init__(self):
        sar=Popen('sar -B 1 1', shell=True, stdout=PIPE, stderr=PIPE)
        (sout,serr) = sar.communicate()
        self.Average = sout.split('\n')[-2]
        self.pgpgin = self.Average.split()[1]
        self.pgpgout = self.Average.split()[2]
        self.fault = self.Average.split()[3]
        self.majflt = self.Average.split()[4]
        self.pgfree = self.Average.split()[5]
        self.pgscank = self.Average.split()[6]
        self.pgscand = self.Average.split()[7]
        self.pgsteal = self.Average.split()[8]
        self.vmeff = self.Average.split()[9]


stat = Paging()
print stat.Average
print stat.pgpgin,stat.pgpgout,stat.fault,stat.majflt,stat.pgfree,stat.pgscank,stat.pgscand,stat.pgsteal,stat.vmeff
