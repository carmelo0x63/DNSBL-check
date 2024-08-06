#!/usr/bin/env python3
import argparse
import dns.resolver
import sys
from DNSBL_list import DOMAINS

# Global variables
__version__ = '2.0.0'
__build__ = '20240722'

# ANSI color codes
class ANSI:
    RESET     = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY      = '\033[90m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    ORANGE    = '\033[93m'
    BLUE      = '\033[94m'
    HEADER    = '\033[95m'


def dnsbl_check(input_ip, dnsbl):
    reversed_ip = '.'.join(reversed(input_ip.split('.')))
    lookup = reversed_ip + '.' + dnsbl
    try:
        query_a = dns.resolver.resolve(lookup, 'A')
        if query_a:
#            print(f'ANSI.GREEN{input_ip} is blacklisted on {dnsbl}: {response[0].host}ANSI.RESET')
            print(f'{ANSI.GREEN}{input_ip} is blacklisted on {dnsbl}{ANSI.RESET}')
            if IS_VERBOSE:
                query_txt = dns.resolver.resolve(lookup, 'TXT')
                print(f'{ANSI.GREEN}╰─ ➤ {str(query_txt.response.answer[0])}{ANSI.RESET}')
        else:
            if IS_VERBOSE:
                print(f'{ANSI.RED}{input_ip} has no reply from {dnsbl}{ANSI.RESET}')
        return False
    except dns.resolver.NXDOMAIN as e:
        if IS_VERBOSE:
            print(f'{ANSI.RED}{input_ip} received NXDOMAIN: {e}{ANSI.RESET}')
    except dns.resolver.Timeout:
        if IS_VERBOSE:
            print(f'{ANSI.RED}{input_ip} received NXDOMAIN: {e}{ANSI.RESET}')
    except dns.resolver.NoAnswer:
        if IS_VERBOSE:
            print(f'{ANSI.RED}{input_ip} received NXDOMAIN: {e}{ANSI.RESET}')
    except dns.resolver.NoNameservers:
        if IS_VERBOSE:
            print(f'{ANSI.RED}{input_ip} received NXDOMAIN: {e}{ANSI.RESET}')


def main():
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

    # A global variable is instantiated in case of -v/--verbose argument
    global IS_VERBOSE
    IS_VERBOSE = args.verbose

    for dnsbl in DOMAINS:
#        response = dnsbl_check(args.input, dnsbl)
        dnsbl_check(args.input, dnsbl)
#        if response:
#            print(response)

if __name__ == '__main__':
    main()

