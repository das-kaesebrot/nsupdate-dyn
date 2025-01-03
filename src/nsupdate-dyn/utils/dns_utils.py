import json
import logging
import socket
import subprocess
from typing import Optional
from ..classes.query_type import DNSQueryType

_logger = logging.getLogger("dns_utils")


def check_for_ip_change_via_python_libs(
    domain: str, http_self_resolver: str, dns_server: str
) -> Optional[str]:

    import requests
    import dns.resolver

    resp_http_resolver = requests.get(http_self_resolver)
    self_resolved_ip = resp_http_resolver.text
    resolver_answer = dns.resolver.resolve_at(dns_server, domain, "A")
    resolver_answer_list = []

    for rr in resolver_answer:
        resolver_answer_list.append(rr.target.to_text(True))

    return _check_for_ip_change(resolver_answer_list, self_resolved_ip)


def check_for_ip_change_via_system_utils(
    domain: str, http_self_resolver: str, dns_server: str
) -> Optional[str]:
    resp_http_resolver = subprocess.run(
        ["curl", "-4", http_self_resolver], capture_output=True
    )
    self_resolved_ip = resp_http_resolver.stdout.decode().strip()
    resolver_answer = subprocess.run(
        ["dig", "+short", domain, f"@{dns_server}", "A"], capture_output=True
    )
    resolver_answer_list = resolver_answer.stdout.decode().strip().split("\n")

    return _check_for_ip_change(resolver_answer_list, self_resolved_ip)


def _check_for_ip_change(resolver_answer_list, self_resolved_ip: str) -> Optional[str]:
    ip_on_server = None

    _logger.debug(f"Self resolved IP: {self_resolved_ip}")
    _logger.debug(f"Existing IPs resolved from server: {resolver_answer_list}")
    
    if len(resolver_answer_list) > 0:
        ip_on_server = resolver_answer_list[0]
    
    if not ip_on_server or ip_on_server != self_resolved_ip:
        # if there is no response, we can safely assume that we have to set the record
        _logger.debug("IP change detected")
        return self_resolved_ip

    return None


def update_a_record(
    dnskey: dict, host: str, subdomains: str | list[str], new_ip: str, zone: str, query_type_str: str
):
    import dns.update
    import dns.query
    import dns.tsigkeyring
    
    query_type = DNSQueryType(query_type_str)

    keyring = dns.tsigkeyring.from_text(dnskey)

    if isinstance(subdomains, str):
        subdomains = [subdomains]

    # add . suffix to make it an absolute domain
    if not zone.endswith("."):
        zone = f"{zone}."

    update = dns.update.Update(zone, keyring=keyring)
    for subdomain in subdomains:
        update.replace(subdomain, 300, "A", new_ip)

    _logger.debug(f"Update to be sent:\n{update}")

    host_ip = resolve_host_to_ip(host)
    
    response = None
    
    if query_type == DNSQueryType.TLS:
        response = dns.query.tls(update, host_ip, timeout=10, server_hostname=host)
    elif query_type == DNSQueryType.TCP:
        response = dns.query.tcp(update, host_ip, timeout=10)
    elif query_type == DNSQueryType.UDP:
        response = dns.query.udp(update, host_ip, timeout=10)
    else:
        raise NotImplementedError(f"Query type '{query_type}' is not supported yet")
    
    _logger.debug(f"Nameserver response:\n{response.to_text()}")
    
    if len(response.errors) > 0:
        raise RuntimeError(f"Updating DNS entries failed:\n{''.join(response.errors)}")


def get_dnskey_dict(key_file: str) -> dict:
    with open(key_file, "r") as f:
        return json.load(f)


def resolve_host_to_ip(host: str) -> str:
    resp = socket.getaddrinfo(host, None, proto=socket.IPPROTO_IP)
    _logger.debug(resp[0])
    return resp[0][-1][0]  # hacky but it might just work

# creates an FQDN without trailing dot
def get_fqdn(domain: str, zone: str) -> str:
    if not domain.endswith("."):
        domain = f"{domain}.{zone}"
    
    # remove the trailing dot, no matter what
    if domain.endswith("."):
        domain = domain[:-1]
    
    return domain