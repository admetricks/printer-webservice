FROM        ubuntu:14.04

RUN         sed -i "/^# deb.*multiverse/ s/^# //" /etc/apt/sources.list
RUN         apt-get update && apt-get install -y fonts-wqy-zenhei fonts-thai-tlwg fontconfig libfontconfig1 libfreetype6 libjpeg-turbo8 libx11-6 libxext6 libxrender1 wget xvfb python3 python3-pip xfonts-75dpi flashplugin-installer

RUN         wget -O wkhtmltox.deb http://downloads.sourceforge.net/project/wkhtmltopdf/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb
RUN         dpkg -i wkhtmltox.deb
ADD         wkhtmltopdf.sh /usr/bin/wkhtmltopdf.sh

RUN         useradd printer_service

ADD         requirements.txt /app/requirements.txt
ADD         run.py           /app/run.py
ADD         app.py           /app/app.py

RUN         pip3 install -r /app/requirements.txt

EXPOSE      8080

USER        printer_service

ENTRYPOINT ["python3"]

CMD        ["/app/run.py"]
