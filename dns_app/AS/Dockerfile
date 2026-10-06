# Qikai Yang (qy1166) - DCN Lab 3 - AS image
FROM python:3.11-slim
WORKDIR /app
COPY as_server.py .
RUN mkdir -p /app/data
EXPOSE 53533/udp
CMD ["python", "-u", "as_server.py"]
