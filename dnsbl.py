#!/usr/bin/env python3
# Originally developed by acidvegas in Python (https://git.acid.vegas/proxytools)
# dnsbl.py: script to verify whether one or more IP addresses have been blacklisted
# author: Carmelo C
# email: carmelo.califano@gmail.com
# history, date format ISO 8601:
#   2024-07-19: 1.0 list of DNSBL moved to external file (DNSBL_list)
#               fixed handling of text input file (args.input -> ip)
#               added a check to fallback to `help` (`-h`) in case of no arguments
#               added -V/--version option

import argparse      # parser for command-line options, arguments and sub-commands
import asyncio       # library to write concurrent code using the async/await syntax
import ipaddress     # create, manipulate and operate on IPv4 and IPv6 addresses and networks
import logging       # functions and classes which implement a flexible event logging system for applications and libraries
import os            # miscellaneous operating system interfaces
import sys           # access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter
from DNSBL_list import DOMAINS

try:
    import aiodns
except ImportError:
    raise SystemExit('[!] Missing required library \'aiodns\' (https://pypi.org/project/aiodns/)')

# Global variables
__version__ = '1.0.0'
__build__ = '20240719'

# ANSI color codes
RED   = '\033[91m'
GREEN = '\033[92m'
GREY  = '\033[90m'
RESET = '\033[0m'


async def check_dnsbl(ip: str, dnsbl: str, semaphore: asyncio.Semaphore):
    '''
    Check if an IP address is blacklisted on a DNSBL.
    
    :param ip: IP address to check.
    :param dnsbl: DNSBL to check.
    :param semaphore: Semaphore to limit the number of concurrent requests.
    '''
    async with semaphore:
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


async def query_dnsbl(ip, concurrency):
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [check_dnsbl(ip, dnsbl, semaphore) for dnsbl in DOMAINS]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'DNSBL Lookup Tool, version ' + __version__ + ', build ' + __build__ + '.')
    parser.add_argument('input', help = 'IP address or file with IP addresses')
    parser.add_argument('-c', '--concurrency', type = int, default = 20, help = 'Number of concurrent lookups')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Enable verbose output')
    parser.add_argument('-V', '--version', action = 'version', version = '%(prog)s ' + __version__)

    # In case of no arguments prints help message then exits
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args() # else parse command line

    try:
        ipaddress.ip_address(args.input)
        asyncio.run(query_dnsbl(args.input, args.concurrency))
    except:
        if os.path.isfile(args.input):
            with open(args.input, 'r') as file:
                for line in file:
                    ip = line.strip()
                    try:
                        ipaddress.ip_address(ip)
                        asyncio.run(query_dnsbl(ip, args.concurrency))
                    except:
                        logging.warning(f'Invalid IP address: {ip}')
        else:
            raise SystemExit(f'Invalid IP address or file: {args.input}')

