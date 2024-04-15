#!/usr/bin/env python3
import argparse
import json
import logging
from .classes.config import Config
from .utils.dns_utils import check_for_ip_change_via_system_utils, update_a_record


def main():
    # set up logging config via argparse
    available_levels = [
        level.lower() for level in logging.getLevelNamesMapping().keys()
    ]
    available_levels.remove(logging.getLevelName(logging.NOTSET).lower())
    available_levels.remove(logging.getLevelName(logging.WARNING).lower())

    parser = argparse.ArgumentParser(description="Dynamic DNS updater for bind9")
    parser.add_argument(
        "-l",
        "--logging",
        help="set the log level",
        dest="loglevel",
        type=str,
        choices=available_levels,
        default=logging.getLevelName(logging.INFO).lower(),
    )
    
    parser.add_argument(
        "-c",
        "--config",
        help="set the config path",
        type=str,
        default="/etc/nsupdate-dyn/config.json"
    )
    
    parser.add_argument("-d", "--dry-run", help="don't actually update anything but show what would be done", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        level=args.loglevel.upper(),
    )
    logger = logging.getLogger("main")

    try:
        config = Config.from_json(args.config)
        dnskey = config.get_dnskey_dict()

        logger.debug(f"Config: {json.dumps(config.as_dict())}")

        new_ip = None

        for domain in config.domains_to_update:
            logger.debug()
            new_ip = check_for_ip_change_via_system_utils(
                domain=domain,
                http_self_resolver=config.ip_resolver,
                dns_server=config.server,
            )

        if new_ip and not args.dry_run:
            logger.info("Change detected, updating records")
            update_a_record(
                dnskey=dnskey,
                host=config.server,
                subdomains=config.domains_to_update,
                new_ip=new_ip,
                zone=config.zone,
            )

    except KeyboardInterrupt:
        logger.info("Stopping updater")
        exit(0)

    except Exception as e:
        logger.exception("Fatal exception encountered")
        exit(1)


if __name__ == "__main__":
    main()
