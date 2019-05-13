FROM python:3.7
RUN apt-get update && apt-get install bison flex libwww-perl subversion -y
RUN svn co http://svn.code.sf.net/p/cwb/code/cwb/trunk cwb && svn co http://svn.code.sf.net/p/cwb/code/perl/trunk cwb-perl
WORKDIR /cwb/
RUN ./install-scripts/install-linux
ENV PATH="/usr/local/cwb-3.4.15/bin:${PATH}"
WORKDIR /cwb-perl/CWB
RUN perl Makefile.PL --config=/usr/local/cwb-3.4.15/bin/cwb-config && make && make test && make install
RUN mkdir /app /cwb/registry /cwb/data
ENV CORPUS_REGISTRY="?/cwb/registry:?/usr/local/cwb-3.4.15/share/cwb/registry/"
ADD . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system
WORKDIR /app/cwb_parallel