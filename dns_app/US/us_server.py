# Qikai Yang (qy1166) - DCN Lab 3 - User Server (US)
# HTTP server on port 8080.
#   GET /fibonacci?hostname=...&fs_port=...&number=...&as_ip=...&as_port=...
#   1) resolve hostname via the Authoritative Server (UDP)  2) query FS  3) return result
import socket

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
PARAMS = ("hostname", "fs_port", "number", "as_ip", "as_port")


def parse_message(text):
    fields = {}
    for token in text.split():
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key.upper()] = value
    return fields


def dns_query(hostname, as_ip, as_port):
    """Send a simplified DNS query to AS and return the IP address (or None)."""
    message = f"TYPE=A\nNAME={hostname}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    try:
        sock.sendto(message.encode("utf-8"), (as_ip, as_port))
        reply, _ = sock.recvfrom(2048)
    finally:
        sock.close()
    return parse_message(reply.decode("utf-8")).get("VALUE")


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    args = {k: request.args.get(k) for k in PARAMS}
    missing = [k for k, v in args.items() if not v]
    if missing:
        return jsonify(error=f"missing parameters: {', '.join(missing)}"), 400
    try:
        fs_port, as_port = int(args["fs_port"]), int(args["as_port"])
    except ValueError:
        return jsonify(error="fs_port and as_port must be integers"), 400

    try:
        fs_ip = dns_query(args["hostname"], args["as_ip"], as_port)
    except (socket.timeout, OSError) as e:
        return jsonify(error=f"DNS query to AS failed: {e}"), 502
    if not fs_ip:
        return jsonify(error=f"hostname {args['hostname']} not found"), 404

    try:
        r = requests.get(f"http://{fs_ip}:{fs_port}/fibonacci",
                         params={"number": args["number"]}, timeout=5)
    except requests.RequestException as e:
        return jsonify(error=f"request to FS failed: {e}"), 502
    # pass FS status through (200 with the value, or 400 for a bad number)
    return r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "text/plain")}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
