FROM ubuntu:18.04

RUN apt-get update && apt-get install -y apt-utils python3 python3-pip autoconf dh-autoreconf libssl-dev build-essential automake pkg-config libtool libffi-dev libgmp-dev libsecp256k1-dev
RUN apt-get install -y software-properties-common && add-apt-repository ppa:ethereum/ethereum && apt-get update && apt-get install -y solc
RUN pip3 install --upgrade setuptools

RUN mkdir -p /src/app/
COPY . /src/app
WORKDIR /src/app

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]
