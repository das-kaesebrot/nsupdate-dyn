package rfc2136updater

type DNSTransport int

const (
	DNSTransportUDP DNSTransport = iota
	DNSTransportTCP
	DNSTransportTLS
	DNSTransportHTTPS
)

var transportName = map[DNSTransport]string{
	DNSTransportUDP:   "udp",
	DNSTransportTCP:   "tcp",
	DNSTransportTLS:   "tls",
	DNSTransportHTTPS: "https",
}

func (dt DNSTransport) String() string {
	return transportName[dt]
}
