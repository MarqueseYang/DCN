# Qikai Yang (qy1166) - DCN Lab 3 - Authoritative Server (AS)
# UDP server on port 53533.
#   Registration:  "TYPE=A\nNAME=<name> VALUE=<ip> TTL=<ttl>\n"  -> stored in a JSON file
#   DNS query:     "TYPE=A\nNAME=<name>\n"                         -> "TYPE=A\nNAME=<name> VALUE=<ip> TTL=<ttl>\n"
import json
import os
import socket
import threading

HOST = "0.0.0.0"
PORT = 53533
DB_FILE = os.environ.get("AS_DB_FILE", "/app/data/dns_records.json")
_lock = threading.Lock()


def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_db(db):
    os.makedirs(os.path.dirname(DB_FILE) or ".", exist_ok=True)
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f, indent=2)
    os.replace(tmp, DB_FILE)  # atomic write


def parse_message(text):
    """Parse 'KEY=VALUE' tokens separated by spaces/newlines into a dict."""
    fields = {}
    for token in text.split():
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key.strip().upper()] = value.strip()
    return fields


def format_record(rtype, name, value, ttl):
    return f"TYPE={rtype}\nNAME={name} VALUE={value} TTL={ttl}\n"


def handle(message):
    fields = parse_message(message)
    rtype, name = fields.get("TYPE"), fields.get("NAME")
    if not rtype or not name:
        return "ERROR=BAD_REQUEST\n"

    # Registration request: contains VALUE (and TTL)
    if "VALUE" in fields:
        ttl = fields.get("TTL", "10")
        with _lock:
            db = load_db()
            db[f"{rtype}:{name}"] = {"type": rtype, "name": name,
                                     "value": fields["VALUE"], "ttl": ttl}
            save_db(db)
        print(f"[AS] registered {name} -> {fields['VALUE']} (TTL={ttl})", flush=True)
        return format_record(rtype, name, fields["VALUE"], ttl)

    # DNS query: only TYPE and NAME
    with _lock:
        record = load_db().get(f"{rtype}:{name}")
    if record is None:
        print(f"[AS] query {name}: not found", flush=True)
        return f"TYPE={rtype}\nNAME={name} ERROR=NOT_FOUND\n"
    print(f"[AS] query {name} -> {record['value']}", flush=True)
    return format_record(record["type"], record["name"], record["value"], record["ttl"])


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[AS] listening on UDP {HOST}:{PORT}, db={DB_FILE}", flush=True)
    while True:
        data, addr = sock.recvfrom(2048)
        reply = handle(data.decode("utf-8", errors="replace"))
        sock.sendto(reply.encode("utf-8"), addr)


if __name__ == "__main__":
    main()
