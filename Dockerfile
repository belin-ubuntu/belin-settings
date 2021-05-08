from ubuntu:18.04 AS builder
env DEBIAN_FRONTEND=noninteractive container=belin_team LC_ALL=C
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
apt-get install -y --no-install-recommends software-properties-common && \
add-apt-repository main && \
add-apt-repository restricted && \
add-apt-repository universe && \
add-apt-repository multiverse && \
add-apt-repository "deb http://archive.canonical.com/ubuntu $(lsb_release -sc) partner" && \
add-apt-repository -r "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc)-backports main restricted universe multiverse" && \
dpkg --add-architecture i386 && \
add-apt-repository -y ppa:belin/stable && \
apt-get update && \
sed -i '/deb-src/s/^# //' /etc/apt/sources.list && apt update && \
apt-get clean && apt-get autoclean && \
sed -i '/deb-src/s/^# //' /etc/apt/sources.list.d/* && apt update && \
apt-get -y dist-upgrade && \
apt-get -y build-dep --no-install-recommends belin-desktop && \
apt-get -y build-dep --no-install-recommends belin-settings && \
apt-get -y --no-install-recommends install dh-make gem2deb npm2deb git-buildpackage && \
ln -sf /usr/share/zoneinfo/Europe/Budapest /etc/localtime && dpkg-reconfigure --frontend noninteractive tzdata && \
apt-get -y autoremove --purge && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*
add . /usr/src/belin-settings
workdir /usr/src/belin-settings
gbp buildpackage -S
gbp buildpackage
