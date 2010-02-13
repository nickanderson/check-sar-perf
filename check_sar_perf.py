#!/usr/bin/env python
import os
import sys
import re
from subprocess import *


os.environ['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin'
#Nagios return code level
# 0 - OK       - The plugin was able to check the service and it appeared to be functioning properly 
# 1 - WARNING  - The plugin was able to check the service, but it appeared to be above some "warning" 
#                threshold or did not appear to be working properly
# 2 - CRITICAL - The plugin detected that either the service was not running or it was above some "critical" threshold
# 3 - UNKNOWN  - Invalid command line arguments were supplied to the plugin or low-level failures 
#                internal to the plugin (such as unable to fork, or open a tcp socket) that prevent 
#                it from performing the specified operation. Higher-level errors (such as name 
#                resolution errors, socket timeouts, etc) are outside of the control of plugins and 
#                should generally NOT be reported as UNKNOWN states. 

class SarNRPE:
    '''Call sar and parse statistics returning in NRPE format'''
    def __init__(self, command, device=None):
        sar=Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (sout,serr) = sar.communicate()
        if device == None:
            (columns, data) = self.SortOutput(sout)
        else:
            (columns, data) = self.SortCombinedOutput(sout, device)

        self.Parser(columns, data)

    def SortOutput(self, sarout):
        data = sarout.split('\n')[-2].split()
        # remove 'Average:'
        data.pop(0)
        columns = sarout.split('\n')[-4].split()
        # Remove Timestamp
        columns.pop(0)
        columns.pop(0)
        return (columns, data)

    def SortCombinedOutput(self, sarout, device):
        '''Sort output from sar command, return columns and relevant data'''
        find_columns = True
        mycolumns = []
        mydata = []
        search = re.compile('^Average:')
        for line in sarout.split('\n'):
            if search.match(line):
                if find_columns:
                    mycolumns.append(line)
                    find_columns = False
                else:
                    mydata.append(line)
        search = re.compile('^Average:\s.*%s\s.*' %device)
        for line in mydata:
            if not search.match(line):
                mydata.remove(line)
        mycolumns = mycolumns[0].split()
        mydata = mydata[0].split()
        mycolumns.pop(0)
        mydata.pop(0)
        return (mycolumns,mydata)

    def Parser(self, columns, data):
        '''Sar parser to construct nrpe formatted device'''
        self.stats = []
        # Create dictionary
        for i in range(len(columns)):
            string = "%s=%s" %(columns[i].strip('%'), data[i].strip())
            self.stats.append(string)

def CheckBin(program):
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
           not os.path.isdir(os.path.join(path, program)):
               return os.path.join(path, program)
               #return True
    return False


def Main(args):
    if not len(args) > 1:
        print 'ERROR: no profile selected'
        sys.exit(3)
    if not CheckBin('sar'):
        print 'ERROR: sar not found on PATH (%s), install sysstat' %os.environ['PATH']
        sys.exit(2)

    myOpts = {}
    myOpts['paging'] = 'sar -B 1 1'
    myOpts['cpu'] = 'sar -C 1 1'
    myOpts['memory_util'] = 'sar -r 1 1'
    myOpts['memory_stat'] = 'sar -R 1 1'
    myOpts['io_transfer'] = 'sar -b 1 1'
    myOpts['queueln_load'] = 'sar -q 1 1'
    myOpts['swap_util'] = 'sar -S 1 1'
    myOpts['swap_stat'] = 'sar -W 1 1'
    myOpts['kernel'] = 'sar -v 1 1'
    myOpts['disk'] = 'sar -d -p 1 1'

    if args[1] in myOpts:
        if args[1] == 'disk':
            if len(args) > 2:
                sar = SarNRPE(myOpts[args[1]],args[2])
            else:
                print 'ERROR: no device specified'
                sys.exit(3)
        else:
            sar = SarNRPE(myOpts[args[1]])
    else:
        print 'ERROR: option not defined'
        sys.exit(3)
    # Output in NRPE format
    print 'sar OK|', ' '.join(sar.stats)

if __name__ == '__main__':
    Main(sys.argv)
