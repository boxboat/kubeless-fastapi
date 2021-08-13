FROM bitnami/minideb-runtimes:stretch

# Install required system packages and dependencies
RUN install_packages build-essential ca-certificates curl git libbz2-1.0 libc6 libffi6 libncurses5 libreadline7 libsqlite3-0 libssl1.1 libtinfo5 pkg-config unzip wget zlib1g
RUN wget -nc -P /tmp/bitnami/pkg/cache/ https://downloads.bitnami.com/files/stacksmith/python-3.8.6-5-linux-amd64-debian-9.tar.gz && \
    echo "a9d49f7386efa7bbf4efe347244d5c5202dcf9a89b4b749c0c58904a83f0c18f  /tmp/bitnami/pkg/cache/python-3.8.6-5-linux-amd64-debian-9.tar.gz" | sha256sum -c - && \
    tar -zxf /tmp/bitnami/pkg/cache/python-3.8.6-5-linux-amd64-debian-9.tar.gz -P --transform 's|^[^/]*/files|/opt/bitnami|' --wildcards '*/files' && \
    rm -rf /tmp/bitnami/pkg/cache/python-3.8.6-5-linux-amd64-debian-9.tar.gz

ENV BITNAMI_APP_NAME="python" \
    BITNAMI_IMAGE_VERSION="3.8.6-5" \
    PATH="/opt/bitnami/python/bin:$PATH"

RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
RUN python ./get-pip.py

RUN pip install fastapi==0.65.2 uvicorn==0.14.0 fastapi-versioning==0.9.1 starlette==0.14.2 pydantic prometheus_client

WORKDIR /
ADD _kubeless.py .

USER 1000

ENV PYTHONUNBUFFERED 1
CMD ["python", "/_kubeless.py"]