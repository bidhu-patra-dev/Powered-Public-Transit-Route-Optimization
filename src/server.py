"""Dual-stack (IPv4 + IPv6) Uvicorn server entrypoint for cloud and local deployments."""

import os
import socket
import uvicorn


def _create_dual_stack_socket(port: int) -> socket.socket:
    """Bind a TCP socket accepting both IPv4 and IPv6 traffic, falling back to IPv4."""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        sock.bind(("::", port))
        sock.listen(128)
        sock.set_inheritable(True)
        return sock
    except OSError:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(128)
        sock.set_inheritable(True)
        return sock


def main() -> None:
    """Start the FastAPI app on Railway's dynamic PORT (default 8000) across IPv4/IPv6."""
    raw_port = os.environ.get("PORT", "").strip()
    port = int(raw_port) if raw_port.isdigit() else 8000
    print(f"Booting CTA Transit AI server on dual-stack [::]+0.0.0.0 port {port} (env PORT={raw_port or 'unset'})", flush=True)
    sock = _create_dual_stack_socket(port)
    config = uvicorn.Config("src.api:app", log_level="info")
    server = uvicorn.Server(config)
    server.run(sockets=[sock])


if __name__ == "__main__":
    main()
