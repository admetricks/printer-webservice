FROM        ubuntu:14.04

RUN         sed -i "/^# deb.*multiverse/ s/^# //" /etc/apt/sources.list
RUN         apt-get update -qq && \
            apt-get install -yqq fonts-wqy-zenhei fonts-thai-tlwg fontconfig libfontconfig1 libfreetype6 libjpeg-turbo8 libx11-6 libxext6 libxrender1 wget xvfb python3 python3-pip xfonts-75dpi flashplugin-installer && \
            apt-get -yqq clean

RUN         wget -O wkhtmltox.tar.xz https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && \
            tar xf wkhtmltox.tar.xz && \
            mv wkhtmltox/bin/wkhtmltopdf  /usr/local/bin/wkhtmltopdf

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
