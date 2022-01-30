import os
import subprocess
import sys

def main():
    scriptName="nsupdate-dyn"
    absScriptPath=os.path.join(os.path.abspath(os.path.dirname(__file__)), scriptName + ".py")

    systemdUnitFileContent = f"""
[Unit]
Description={scriptName} python3 script
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 "{absScriptPath}" --systemd

[Install]
WantedBy=multi-user.target
"""
    with open(os.path.join("/etc/systemd/system", scriptName + ".service"), mode='w') as f:
        f.write(systemdUnitFileContent)
        
    cmdBase = "systemctl"
    ops = [["daemon-reload"], ["enable", scriptName], ["restart", scriptName], ["status", scriptName]]
    
    for entry in ops:
        cmd = [cmdBase]
        cmd.extend(entry)
        subprocess.run(cmd)


if __name__ == "__main__":
    if os.path.exists("/run/systemd/system"):
        main()
    else:
        print("Path /run/systemd/system not found, aborting install")
        sys.exit(1)