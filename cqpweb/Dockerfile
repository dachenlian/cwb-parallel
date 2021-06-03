FROM httpd:2.4.48
RUN echo "deb  http://deb.debian.org/debian  stretch main" >> /etc/apt.sources.list \
    && echo "deb-src  http://deb.debian.org/debian  stretch main" >> /etc/apt.sources.list \
    && apt-get update \
    && apt-get install -y wget \
    && apt-get -y install lsb-release apt-transport-https ca-certificates \
    && wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg \
    && echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/php.list
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install bison pkg-config libglib2.0-dev libglib2.0-0 flex libncurses5-dev libncursesw5-dev \
    php7.4 php7.4-cli php7.4-gd php7.4-intl php7.4-json php7.4-mbstring php7.4-mysqli php7.4-phar php7.4-zip php7.4-mysql php7.4-common \
    php7.4-fpm php7.4-curl php7.4-xml php-pear php7.4-bcmath libapache2-mod-php7.4 \
    libpcre3 libpcre3-dev perl libreadline6-dev vim nano build-essential -y --no-install-recommends
# apt-get installs modules in another place so must move the new ones to where the existing ones are located
RUN mv /usr/lib/apache2/modules/* /usr/local/apache2/modules
RUN mkdir --parents /cwb/registry /cwb/data /cwb/tmp /cwb/uploads
COPY CQPweb-3.2.43 /usr/local/apache2/htdocs
COPY cwb-3.4.22 /cwb/cwb-3.4.22
COPY cwb-perl /cwb/cwb-perl
# avoid permission issues with CQPweb without
RUN chown -R www-data:www-data /cwb /usr/local/apache2 \
    && chmod ugo+rwx -R /cwb /usr/local/apache2 
WORKDIR /cwb/cwb-3.4.22/
RUN ./install-scripts/install-linux
WORKDIR /cwb/cwb-perl/CWB
RUN perl Makefile.PL --config=/usr/local/cwb-3.4.22/bin/cwb-config \
    && make \
    && make test \
    && make install
WORKDIR /cwb/cwb-perl/CWB-CL
RUN perl Makefile.PL --config=/usr/local/cwb-3.4.22/bin/cwb-config \
    && make \
    && make test \
    && make install
ENV CORPUS_REGISTRY=/cwb/registry
ENV PATH=$PATH:/usr/local/cwb-3.4.22/bin
COPY conf/config.inc.php /usr/local/apache2/htdocs/lib/
WORKDIR /usr/local/apache2/htdocs/