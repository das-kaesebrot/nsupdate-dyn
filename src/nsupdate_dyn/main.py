#!/usr/bin/env python3
import argparse
import json
import logging

from .classes.query_type import DNSQueryType

# default values
ARG_SILENT = False
ARG_IP_RESOLVER = "http://ifconfig.co/ip"
ARG_QUERY_TYPE = DNSQueryType.TLS


def main():
    # set up logging config via argparse
    available_levels = [
        level.lower() for level in logging.getLevelNamesMapping().keys()
    ]
    available_levels.remove(logging.getLevelName(logging.NOTSET).lower())
    available_levels.remove(logging.getLevelName(logging.WARNING).lower())

    parser = argparse.ArgumentParser(
        description="Dynamic DNS updater for bind9",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        help="Don't actually update anything but show what would be done",
        action="store_true",
    )

    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress non-essential logging (so that it runs silently in a cron job). Overrides the setting of the log level argument.",
        required=False,
        default=ARG_SILENT,
    )

    parser.add_argument(
        "-l",
        "--logging",
        help="Set the log level",
        dest="loglevel",
        type=str,
        choices=available_levels,
        default=logging.getLevelName(logging.INFO).lower(),
    )

    parser.add_argument(
        "-k", "--key-file", help="TSIG key file to use", type=str, required=True
    )

    parser.add_argument(
        "-r",
        "--ip-resolver",
        help="HTTP based resolver to use for getting own IPv4 address",
        type=str,
        required=False,
        default=ARG_IP_RESOLVER,
    )

    parser.add_argument(
        "-s",
        "--server",
        help="Nameserver to update A record(s) at",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-z",
        "--zone",
        help="DNS zone to update A record(s) in",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-f",
        "--force",
        help="Force update A record(s) on server, even if IP didn't change",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--domains",
        nargs="*",
        help="Subdomains to update A record(s) for",
        required=True,
    )
    parser.add_argument(
        "-q",
        "--query-type",
        help="Query type to use",
        required=True,
        choices=DNSQueryType.list(),
        default=DNSQueryType.TLS,
        type=str
    )

    args = parser.parse_args()
    
    logging.basicConfig(
        format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        level=args.loglevel.upper(),
    )
    
    logging.getLogger("main").debug(f"Args: {json.dumps(vars(args), indent=4)}")
    
    run_update(**vars(args))
        
def run_update(loglevel: str, key_file: str, server: str, zone: str, domains: list[str], force: bool = False, dry_run: bool = False, silent: bool = False, ip_resolver: str = ARG_IP_RESOLVER, query_type: str = ARG_QUERY_TYPE):    
    
    # import later on so that we can call a subparser without the required packages
    from .utils.dns_utils import check_for_ip_change_via_system_utils, update_a_record, get_dnskey_dict, get_fqdn
    
    logger = logging.getLogger("main")

    if silent:
        logger.setLevel(logging.WARN)
        
    try:
        new_ip = None

        for domain in domains:
            fqdn = get_fqdn(domain, zone)
            
            new_ip = check_for_ip_change_via_system_utils(
                domain=fqdn,
                http_self_resolver=ip_resolver,
                dns_server=server,
            )
            
        if dry_run:
            logger.warning("Dry run detected, skipping update")
            return

        if new_ip or force:
            logger.info("Change detected, updating records")
            update_a_record(
                dnskey=get_dnskey_dict(key_file),
                host=server,
                subdomains=domains,
                new_ip=new_ip,
                zone=zone,
                query_type_str=query_type,
            )

    except KeyboardInterrupt:
        logger.info("Stopping updater")
        exit(0)

    except Exception as e:
        logger.exception("Fatal exception encountered")
        exit(1)


if __name__ == "__main__":
    main()
