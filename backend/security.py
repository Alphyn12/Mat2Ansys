"""
Mat2Ansys - URL security validation utilities.

Provides strict validation to prevent SSRF and off-domain navigation.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse, urlunparse


ALLOWED_MATWEB_HOSTS = {"www.matweb.com", "matweb.com"}


def is_allowed_matweb_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    return hostname.lower() in ALLOWED_MATWEB_HOSTS


def _is_disallowed_ip(ip_text: str) -> bool:
    ip = ipaddress.ip_address(ip_text)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _validate_host_resolution(hostname: str):
    try:
        addr_info = socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ValueError(f"Unable to resolve host '{hostname}'.") from exc

    resolved_ips = {item[4][0] for item in addr_info if item and len(item) >= 5}
    if not resolved_ips:
        raise ValueError(f"Host '{hostname}' did not resolve to any IP address.")

    for ip_text in resolved_ips:
        if _is_disallowed_ip(ip_text):
            raise ValueError("Resolved host points to a non-public IP address.")


def validate_and_normalize_matweb_url(raw_url: str) -> str:
    """
    Validate a MatWeb URL and return a normalized safe URL.

    Rules:
      - HTTPS only
      - Host must be www.matweb.com or matweb.com
      - No embedded credentials
      - No custom port (except implicit 443)
      - Host must resolve to public IPs
    """
    if not isinstance(raw_url, str):
        raise ValueError("Material URL must be a string.")

    candidate = raw_url.strip()
    if not candidate:
        raise ValueError("Material URL cannot be empty.")

    parsed = urlparse(candidate)

    if parsed.scheme.lower() != "https":
        raise ValueError("Only HTTPS MatWeb URLs are allowed.")

    if not parsed.hostname or not is_allowed_matweb_host(parsed.hostname):
        raise ValueError("Only matweb.com material URLs are allowed.")

    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed.")

    if parsed.port not in (None, 443):
        raise ValueError("Custom URL ports are not allowed.")

    _validate_host_resolution(parsed.hostname)

    # Canonicalize to lower-case host and https scheme.
    normalized = parsed._replace(
        scheme="https",
        netloc=parsed.hostname.lower(),
        fragment="",
    )
    return urlunparse(normalized)
