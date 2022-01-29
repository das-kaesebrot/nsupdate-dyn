.DEFAULT_GOAL := install

SCRIPT_NAME = nsupdate-dyn
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

define SERVICECONTENT
[Unit]
Description=nsupdate-dyn python3 script
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 ${ROOT_DIR}/${SCRIPT_NAME}.py

[Install]
WantedBy=multi-user.target
endef
export SERVICECONTENT

install:
	touch /etc/systemd/system/${SCRIPT_NAME}.service
	@echo "$$SERVICECONTENT" > /etc/systemd/system/${SCRIPT_NAME}.service
	systemctl daemon-reload
	systemctl enable --now ${SCRIPT_NAME}