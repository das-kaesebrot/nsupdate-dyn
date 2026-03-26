package rfc2136updater

import (
	"net/netip"
	"net/url"

	"github.com/das-kaesebrot/nsupdate-dyn/pkg/keyfile"
)

type IPv4ResolverConfig struct {
	URL        url.URL
	HTTPMethod string
}

type Rfc2136UpdaterConfig struct {
	TSIGKey      keyfile.TSIGKey
	IPv4Resolver IPv4ResolverConfig
	TargetHost   netip.AddrPort
	Zone         string
	Force        bool
	Domains      []string
	Transport    DNSTransport
}
