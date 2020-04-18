FROM python:3.7-buster

RUN pip install beautifulsoup4 click requests
RUN sed -i 's/DEFAULT@SECLEVEL=2/DEFAULT@SECLEVEL=1/' /etc/ssl/openssl.cnf

