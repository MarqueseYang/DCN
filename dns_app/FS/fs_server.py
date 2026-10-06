# Qikai Yang (qy1166) - DCN Lab 3 - Fibonacci Server (FS)
# HTTP server on port 9090.
#   PUT /register            body: {"hostname","ip","as_ip","as_port"} -> registers with AS over UDP, 201
#   GET /fibonacci?number=X  -> 200 with Fibonacci(X), 400 if X is not a non-negative integer
import socket

from flask import Flask, jsonify, request

app = Flask(__name__)
TTL = 10


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.route("/register", methods=["PUT"])
def register():
    body = request.get_json(silent=True, force=True)
    if not body:
        return jsonify(error="body must be a JSON object"), 400
    missing = [k for k in ("hostname", "ip", "as_ip", "as_port") if not body.get(k)]
    if missing:
        return jsonify(error=f"missing fields: {', '.join(missing)}"), 400
    try:
        as_port = int(body["as_port"])
    except (TypeError, ValueError):
        return jsonify(error="as_port must be an integer"), 400

    message = f"TYPE=A\nNAME={body['hostname']} VALUE={body['ip']} TTL={TTL}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    try:
        sock.sendto(message.encode("utf-8"), (body["as_ip"], as_port))
        reply, _ = sock.recvfrom(2048)
    except (socket.timeout, OSError) as e:
        return jsonify(error=f"registration with AS failed: {e}"), 500
    finally:
        sock.close()

    reply = reply.decode("utf-8")
    if "ERROR" in reply or f"VALUE={body['ip']}" not in reply:
        return jsonify(error="AS rejected registration", as_reply=reply), 500
    return jsonify(message="registered", hostname=body["hostname"], ip=body["ip"]), 201


@app.route("/fibonacci", methods=["GET"])
def fib():
    number = request.args.get("number")
    try:
        n = int(number)
    except (TypeError, ValueError):
        return jsonify(error="number must be an integer"), 400
    if n < 0:
        return jsonify(error="number must be non-negative"), 400
    return str(fibonacci(n)), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
