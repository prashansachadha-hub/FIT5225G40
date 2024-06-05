FROM amazonlinux:1
WORKDIR /
RUN yum update -y && yum install -y gcc openssl-devel ffmpeg libsm6 libxext6 wget tar && yum clean all && rm -rf /var/cache/yum
RUN wget https://www.python.org/ftp/python/3.8.9/Python-3.8.9.tgz
RUN tar -xzvf Python-3.8.9.tgz
WORKDIR /Python-3.8.9
RUN ./configure --enable-optimizations
RUN make install && rm -rf Python-3.8.9 Python-3.8.9.tgz
RUN mkdir /packages
RUN echo "opencv-python-headless" >> /packages/requirements.txt
RUN mkdir -p /packages/opencv-python-3.8/python/lib/python3.8/site-packages
RUN pip3.8 install --no-cache-dir -r /packages/requirements.txt -t /packages/opencv-python-3.8/python/lib/python3.8/site-packages