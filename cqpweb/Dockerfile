FROM ubuntu:focal-20210416
RUN apt-get update
RUN apt-get install bison pkg-config libglib2.0-dev libglib2.0-0 flex libncurses5-dev libncursesw5-dev \
libpcre3 libpcre3-dev libreadline6-dev build-essential -y --no-install-recommends
COPY . /app
WORKDIR /app/cwb-3.4.22/
RUN ./install-scripts/install-linux
# RUN make clean && make depend && make all && make install && make realclean

