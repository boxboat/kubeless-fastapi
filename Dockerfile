FROM python:alpine

# Install required system packages and dependencies
RUN apk add curl git unzip wget ca-certificates

RUN pip install fastapi==0.65.2 uvicorn==0.14.0 fastapi-versioning==0.9.1 starlette==0.14.2 pydantic prometheus_client

WORKDIR /
ADD _kubeless.py .

USER 1000

ENV PYTHONUNBUFFERED 1
CMD ["python", "/_kubeless.py"]
