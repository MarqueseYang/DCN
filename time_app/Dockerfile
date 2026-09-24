# Author: Qikai Yang - DCN (CSCI-GA.2662-001) Lab 2
# Based on the course sample; python:3.5 is end-of-life, so a current slim image is used.
FROM python:3.12-slim

ENV TZ=America/New_York

RUN groupadd -g 799 nyu && \
    useradd -r -u 999 -g nyu nyu

# Set up a working folder and install the pre-reqs
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER nyu

COPY --chown=nyu:nyu . .

EXPOSE 8080

CMD [ "python", "./run.py" ]
