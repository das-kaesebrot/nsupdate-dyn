# nsupdate-dyn

A script to automatically update DNS A records on a bind9 server using a TSIG key.

## Usage

```bash
$ python -m src.nsupdate-dyn -h
usage: __main__.py [-h] [--dry-run] [--silent] [-l {critical,fatal,error,warn,info,debug}] -k KEY_FILE [-r IP_RESOLVER] -s
                   SERVER -z ZONE [-f] -d [DOMAINS ...]

Dynamic DNS updater for bind9

options:
  -h, --help            show this help message and exit
  --dry-run             Don't actually update anything but show what would be done (default: False)
  --silent              Suppress non-essential logging (so that it runs silently in a cron job). Overrides the setting of the
                        log level argument. (default: False)
  -l {critical,fatal,error,warn,info,debug}, --logging {critical,fatal,error,warn,info,debug}
                        Set the log level (default: info)
  -k KEY_FILE, --key-file KEY_FILE
                        TSIG key file to use (default: None)
  -r IP_RESOLVER, --ip-resolver IP_RESOLVER
                        HTTP based resolver to use for getting own IPv4 address (default: http://ifconfig.co/ip)
  -s SERVER, --server SERVER
                        Nameserver to update A record(s) at (default: None)
  -z ZONE, --zone ZONE  DNS zone to update A record(s) in (default: None)
  -f, --force           Force update A record(s) on server, even if IP didn't change (default: False)
  -d [DOMAINS ...], --domains [DOMAINS ...]
                        Subdomains to update A record(s) for (default: None)

```