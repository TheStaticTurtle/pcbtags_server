FROM python:3.9-bullseye
MAINTAINER TheStaticTurtle <samuel@thestaticturtle.fr>

WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive

RUN echo "deb http://deb.debian.org/debian bullseye-backports main contrib non-free" > /etc/apt/sources.list.d/bullseye-backports.list && \
    apt -y update && \
    apt install -t bullseye-backports kicad -y && \
    apt install -y xvfb && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /app

# Kicad X server / profile workaround
ENV DISPLAY=:99
COPY ./tools/kicad/default-profile/ /root/.config/kicad

# Run the damn thing
RUN chmod a+x /app/docker-entrypoint.sh
CMD /app/docker-entrypoint.sh

EXPOSE 80
