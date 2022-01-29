from encodings import utf_8
import os
import sys
import subprocess
import json
import requests
import logging

def genConfig(absDir, confDir, confFileName):
    config = {
        "ip-resolver": "http://ifconfig.co/ip",
        "key": "/path/to/your/key.conf",
        "domains-to-update": [
            "1.dyn.example.com",
            "2.dyn.example.com"
        ],
        "zone": "dyn.example.com",
        "nameserver": "ns1.example.com",
        "update-records": [
            "A",
            "AAAA"
        ]
    }
    os.makedirs(os.path.join(absDir, confDir))
    with open(os.path.join(absDir, confDir, confFileName), mode='w') as f:
        json.dump(obj=config, indent=4, fp=f)


def readInConf(absDir, confDir, confFileName):
    with open(os.path.join(absDir, confDir, confFileName), mode='r') as f:
        config = json.load(f)
    
    if not os.path.isabs(config.get("key")):
        logging.error("key variable needs to be an absolute path, given path: %s" % config.get('key'))
        sys.exit(1)

    return config

def checkIfIpHasChangedAndReturnNewIPs(conf):

    returnDict = {
        "changed": False,
    }

    if "A" in conf.get('update-records'):
        aRecordOnServer = subprocess.run(["dig", "+short", conf.get("domains-to-update")[0], f"@{conf.get('nameserver')}", "A"]).stdout
        aaaaRecordOnServer = subprocess.run(["dig", "+short", conf.get("domains-to-update")[0], f"@{conf.get('nameserver')}", "AAAA"]).stdout


    ipv4Curl = subprocess.run(["curl", "-4", conf.get("ip-resolver")], capture_output=True)
    ipv6Curl = subprocess.run(["curl", "-6", conf.get("ip-resolver")], capture_output=True)

    # check if IPv4 is available and has changed
    if ipv4Curl.returncode == 0:
        returnDict["ipv4"] = ipv4Curl.stdout.decode("utf-8").strip()

    if ipv6Curl.returncode == 1:
        returnDict["ipv6"] = ipv6Curl.stdout.decode("utf-8").strip()

    return returnDict

def main():
    absDir = os.path.abspath(os.path.dirname(__file__))
    confDir = "conf"
    confFileName = "config.json"

    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', encoding="utf-8", level=logging.DEBUG)

    if not os.path.exists(confDir):
        genConfig(absDir, confDir, confFileName)
    
    conf = readInConf(absDir, confDir, confFileName)
    newIPv4, newIPv6 = "", ""


    returnDict = checkIfIpHasChangedAndReturnNewIPs(conf)
    logging.debug(returnDict)
    if returnDict.get('changed') == True:
        if 'ipv4' in returnDict.keys():
            newIPv4 = returnDict.get('ipv4')
        if 'ipv6' in returnDict.keys():
            newIPv6 = returnDict.get('ipv6')


if __name__ == "__main__":
    main()