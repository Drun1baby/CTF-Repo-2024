FROM ubuntu:jammy-20231004

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
        python3.11 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --no-create-home pwn && mkdir -p /home/pwn

COPY ./chall.py /home/pwn/


RUN chown -R root:root /home && \
    find /home -type d -exec chmod 555 {} \; && \
    find /home -type f -exec chmod 444 {} \;

WORKDIR /home/pwn