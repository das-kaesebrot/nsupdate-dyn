import os
import sys
import subprocess
import json
from time import sleep
import logging

def genConfig(absDir, confDir, confFileName):
    config = {
        "interval": 300,
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
        aRecordOnServer = subprocess.run(["dig", "+short", conf.get("domains-to-update")[0], f"@{conf.get('nameserver')}", "A"], capture_output=True)
        aRecordOnServer = aRecordOnServer.stdout.decode("utf-8").strip()
        
    if "AAAA" in conf.get('update-records'):
        aaaaRecordOnServer = subprocess.run(["dig", "+short", conf.get("domains-to-update")[0], f"@{conf.get('nameserver')}", "AAAA"], capture_output=True)
        aaaaRecordOnServer = aaaaRecordOnServer.stdout.decode("utf-8").strip()

    ipv4Curl = subprocess.run(["curl", "-4", conf.get("ip-resolver")], capture_output=True)
    ipv6Curl = subprocess.run(["curl", "-6", conf.get("ip-resolver")], capture_output=True)

    # check if IPv4 is available and has changed
    if ipv4Curl.returncode == 0:
        ipv4Local = ipv4Curl.stdout.decode("utf-8").strip()
        returnDict["ipv4"] = ipv4Local
        if ipv4Local != aRecordOnServer: returnDict["changed"] = True

    # check if IPv6 is available and has changed
    if ipv6Curl.returncode == 0:
        ipv6Local = ipv6Curl.stdout.decode("utf-8").strip()
        returnDict["ipv6"] = ipv6Local
        if ipv6Local != aaaaRecordOnServer: returnDict["changed"] = True

    return returnDict


def generateSTDINForNSUpdate(conf, returnDict):
    newIPv4, newIPv6 = "", ""

    if 'ipv4' in returnDict.keys(): newIPv4 = returnDict.get('ipv4')
    if 'ipv6' in returnDict.keys(): newIPv6 = returnDict.get('ipv6')
    
    deleteStatements = ""
    addStatements = ""

    if "A" in conf.get('update-records'):
        for entry in conf.get('domains-to-update'):
            deleteStatements += f"update delete {entry}. A\n"

    if "AAAA" in conf.get('update-records'):
        for entry in conf.get('domains-to-update'):
            deleteStatements += f"update delete {entry}. AAAA\n"
            

    if "A" in conf.get('update-records') and newIPv4:
        for entry in conf.get('domains-to-update'):
            addStatements += f"update add {entry}. 600 A {newIPv4}\n"

    if "AAAA" in conf.get('update-records') and newIPv6:
        for entry in conf.get('domains-to-update'):
            addStatements += f"update add {entry}. 600 AAAA {newIPv6}\n"

    stdinStr = f"""server {conf.get('nameserver')}
zone {conf.get('zone')}
{deleteStatements}{addStatements}show
send
"""

    logging.debug(stdinStr)

    return stdinStr

def runNSUpdate(conf, stdinStr):
    p = subprocess.run(["nsupdate", "-k", conf.get('key')], capture_output=True, text=True, input=stdinStr)

def main():
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)

    try:
        absDir = os.path.abspath(os.path.dirname(__file__))
        confDir = "conf"
        confFileName = "config.json"

        if not os.path.exists(confDir):
            genConfig(absDir, confDir, confFileName)
        
        conf = readInConf(absDir, confDir, confFileName)
        
        while True:
            returnDict = checkIfIpHasChangedAndReturnNewIPs(conf)
            logging.debug(returnDict)
            if returnDict.get('changed') == True:
                logging.info("Detected IP change, updating records")
                returnDict.pop('changed')

                runNSUpdate(conf, generateSTDINForNSUpdate(conf, returnDict))
            
            else:
                logging.info("No IPs changed since last check")
            
            logging.info(f"Sleeping for {conf.get('interval')}s")
            sleep(conf.get('interval'))

    except KeyboardInterrupt:
        logging.info("Stopping updater")
        sys.exit(0)


main()