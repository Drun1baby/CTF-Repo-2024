FROM ubuntu:jammy-20231004

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
        tini xinetd \
        python3 python3-pip\
    && rm -rf /var/lib/apt/lists/*

COPY ./src /app
COPY ./app.xinetd /etc/xinetd.d/app

RUN mkdir -p /app
WORKDIR /app/

COPY ./src/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN chown -R root:root /app && \
    find /app -type d -exec chmod 555 {} \; && \
    find /app -type f -exec chmod 444 {} \;

EXPOSE 1337

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/sbin/xinetd","-dontfork"]