# dns_app — DCN Lab 3, Problem 2
Qikai Yang (qy1166)

| Folder | Service | Port | Protocol |
|---|---|---|---|
| `AS/` | Authoritative Server | 53533 | UDP |
| `FS/` | Fibonacci Server | 9090 | HTTP |
| `US/` | User Server | 8080 | HTTP |

## Message formats (UDP, AS)
Registration (FS → AS):
```
TYPE=A
NAME=fibonacci.com VALUE=<FS_IP> TTL=10
```
Query (US → AS):
```
TYPE=A
NAME=fibonacci.com
```
Response (AS → US):
```
TYPE=A
NAME=fibonacci.com VALUE=<FS_IP> TTL=10
```
AS tells registrations from queries by the presence of `VALUE`. Records are persisted in `/app/data/dns_records.json`.

## Run with Docker
```bash
docker network create dns_net

docker build -t dns-as ./AS
docker build -t dns-fs ./FS
docker build -t dns-us ./US

docker run -d --network dns_net --name as -p 53533:53533/udp dns-as
docker run -d --network dns_net --name fs -p 9090:9090 dns-fs
docker run -d --network dns_net --name us -p 8080:8080 dns-us

docker network inspect dns_net     # note the IPs of "as" and "fs"
```

Register FS (use the IPs from `docker network inspect`):
```bash
curl -X PUT http://localhost:9090/register \
  -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"<FS_IP>","as_ip":"<AS_IP>","as_port":"53533"}'
# -> 201
```

Query through US:
```bash
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=<AS_IP>&as_port=53533"
# -> 55   (200)
```
Missing parameter → 400; non-integer `number` → 400.

## Kubernetes (extra credit)
```bash
docker build -t YOUR_DOCKERHUB_USER/dns-as:latest ./AS && docker push YOUR_DOCKERHUB_USER/dns-as:latest
docker build -t YOUR_DOCKERHUB_USER/dns-fs:latest ./FS && docker push YOUR_DOCKERHUB_USER/dns-fs:latest
docker build -t YOUR_DOCKERHUB_USER/dns-us:latest ./US && docker push YOUR_DOCKERHUB_USER/dns-us:latest
kubectl apply -f deploy_dns.yml
```
Inside the cluster the services reach each other by Service name:
```bash
curl -X PUT http://<NODE_IP>:30002/register -H "Content-Type: application/json" \
  -d '{"hostname":"fibonacci.com","ip":"fs-service","as_ip":"as-service","as_port":"53533"}'
curl "http://<NODE_IP>:30003/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as-service&as_port=53533"
```
