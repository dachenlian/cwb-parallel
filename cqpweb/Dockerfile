FROM ubuntu:focal-20210416
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install bison pkg-config libglib2.0-dev libglib2.0-0 flex libncurses5-dev libncursesw5-dev \
php7.4 php7.4-cli php7.4-gd php7.4-intl php7.4-json php7.4-mbstring php7.4-mysqli php7.4-phar php7.4-zip php7.4-mysql php7.4-common \
libpcre3 libpcre3-dev perl libreadline6-dev build-essential -y --no-install-recommends
# php-fpm php-curl php-xml php-pear php-bcmath\
COPY . /app
WORKDIR /app/cwb-3.4.22/
RUN ./install-scripts/install-linux
RUN mkdir --parents /app/cwb/registry /app/cwb/data /app/cwb/tmp /app/cwb/uploads
ENV CORPUS_REGISTRY=/app/cwb/registry
ENV PATH=$PATH:/usr/local/cwb-3.4.22/bin

