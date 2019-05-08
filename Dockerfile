FROM debian:stretch

WORKDIR /sup

COPY requirements.txt ./
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY scripts ./scripts
COPY w3cstats ./w3cstats
ENV PYTHONPATH /sup

CMD [ "/sup/scripts/watch-log" ]
