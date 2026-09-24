# time_app — DCN Lab 2 (Qikai Yang)

Flask web server that returns the current time at `/time`.

```bash
docker build -t marquese0318/sample-time-app:latest .
docker run --name sample-time-app -p 8080:8080 -it marquese0318/sample-time-app:latest
curl http://localhost:8080/time
```

Docker Hub image: https://hub.docker.com/r/marquese0318/sample-time-app

## Deploy to Kubernetes (minikube)

```bash
kubectl create deployment sample-time-app --image=docker.io/marquese0318/sample-time-app:latest
kubectl expose deployment/sample-time-app --type="NodePort" --port 8080
kubectl get services            # NodePort
minikube ip                     # worker node IP
curl http://<node-ip>:<node-port>/time
```
