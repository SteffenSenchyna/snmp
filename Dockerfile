FROM python:3.9.2-alpine3.13

RUN apk add gcc musl-dev && \
    pip install --upgrade setuptools
COPY requirements.txt server.py /app/
#Moove into the container app folder k
WORKDIR /app
# Install the required packages
RUN pip install -r requirements.txt
COPY ./mibs/ /usr/local/lib/python3.9/site-packages/pysnmp/smi/mibs
EXPOSE 162/UDP

CMD [ "python", "-u", "server.py" ]
