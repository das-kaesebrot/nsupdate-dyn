package resolver

import "net"

func LookupIPs(host string) ([]net.IP, error) {
	return net.LookupIP(host)
}
