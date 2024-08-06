#!/usr/bin/env python3
# dnsbl_t: script to verify whether one or more IP addresses have been blacklisted, multithreaded
# author: Carmelo C
# email: carmelo.califano@gmail.com
# history, date format ISO 8601:
#   2024-07-19: 2.0, ported from dnsbl.py (async version)
# Adapted from: https://github.com/gh0x0st/python3_multithreading
# Useful link(s): https://gist.github.com/sourceperl/10288663

# Import some modules
import argparse         # parser for command-line options, arguments and sub-commands
import ipaddress        # create, manipulate and operate on IPv4 and IPv6 addresses and networks
import dns
import queue            # synchronized queue class
import subprocess       # subprocess management
import sys              # system-specific parameters and functions
import threading        # thread-based parallelism
import time             # time access and conversions
from DNSBL_list import DOMAINS


# Global variables
__version__ = '2.0'
__build__ = '20240722'


# https://svn.blender.org/svnroot/bf-blender/trunk/blender/build_files/scons/tools/
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def worker():
    while True:
        target = q.get()
        send_ping(target)
        q.task_done()


def send_ping(target):
    icmp_response = subprocess.call(['ping', '-c', ICMPCOUNT, '-W', ICMPWAIT, str(target)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    with thread_lock:
        if icmp_response == 0: 
            print(bcolors.OKGREEN + '[+]' + bcolors.ENDC + f' {target} is UP')
        else:
            if IS_VERBOSE:
                print(bcolors.FAIL + '[-]' + bcolors.ENDC + f' {target} is DOWN')


def check_dnsbl(ip: str, dnsbl: str, semaphore: asyncio.Semaphore):
    '''
    Check if an IP address is blacklisted on a DNSBL.
    
    :param ip: IP address to check.
    :param dnsbl: DNSBL to check.
    :param semaphore: Semaphore to limit the number of concurrent requests.
    '''
    reversed_ip = '.'.join(reversed(ip.split('.')))
    try:
        resolver = aiodns.DNSResolver()
        lookup = f'{reversed_ip}.{dnsbl}'
        for item in await resolver.query(lookup, 'TXT'):
            response = await resolver.query(lookup, 'A')
            if response:
                print(f'{GREEN}{ip} is blacklisted on {dnsbl}: {response[0].host}{RESET}')
            else:
                if args.verbose:
                    print(f'{RED}{ip} has no reply from {dnsbl}{RESET}')
    except aiodns.error.DNSError as e:
        if args.verbose:
            if e.args[0] == 4:
                print(f'{GREY}{ip} is not blacklisted on {dnsbl}{RESET}')
            else:
                print(f'{RED}{ip} errored on {dnsbl} with {lookup}: {e}{RESET}')


def main():
    parser = argparse.ArgumentParser(description='IPv4 ping/ICMP sweeper, version ' + __version__ + ', build ' + __build__ + '.')
    parser.add_argument('input', help = 'IP address or file with IP addresses')
    parser.add_argument('-t', '--threads', metavar = '<threads>', type = int, default = 20, help = 'number of threads (default = 20)')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'print extended information')
    parser.add_argument('-V', '--version', action = 'version', version = '%(prog)s ' + __version__)

    # In case of no arguments shows help message
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(10)  # ERROR: no arguments
    else:
        args = parser.parse_args() # parse command line

    # A global variable is instantiated in case of -v/--verbose argument
    global IS_VERBOSE
    IS_VERBOSE = args.verbose

    # "subnet" is parsed from input and validated with "ipaddress"
    if args.subnet:
        subnet = args.subnet
        try:
            ipaddress.ip_network(subnet)
        except ValueError:
            print(f'[-] {subnet} does not appear to be an IPv4 or IPv6 network')
            sys.exit(20)  # ERROR: input must be an IPv4 subnet

    subnet_valid = ipaddress.ip_network(subnet)

    if not isinstance(subnet_valid, ipaddress.IPv4Network) and IS_VERBOSE:
        print(f'[-] {subnet_valid} is an INVALID IPv4 network address')
        sys.exit(20)  # ERROR: input must be an IPv4 subnet

    for r in range(args.threads):
        t = threading.Thread(target = worker)
        t.daemon = True
        t.start()

    # Start timer before sending tasks to the queue
    start_time = time.time()

    all_hosts = list(ipaddress.ip_network(subnet).hosts())

    if IS_VERBOSE:
        print(f'[!] Creating a task request for each host in {subnet_valid}')

    # send ten task requests to the worker
    for item in all_hosts:
        q.put(item)

    # block until all tasks are done
    q.join()

    if IS_VERBOSE:
        print(f'[!] All workers completed their tasks after {round(time.time() - start_time, 2)} seconds')


if __name__ == '__main__':
    # Define a print lock
    thread_lock = threading.Lock()
    # Create our queue
    q = queue.Queue()

    main()

