# Pull python base image
FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install libpq-dev gcc && apt-get install git postgresql-client -y --no-install-recommends

# Installing requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Copy Project to the container
RUN mkdir -p /fyle-qbo-api
COPY . /fyle-qbo-api/
WORKDIR /fyle-qbo-api

# Do linting checks
RUN flake8 .

#================================================================
# Setup non-root user and permissions
#================================================================
RUN groupadd -r -g 1001 qbo_api_service && \
    useradd -r -g qbo_api_service qbo_api_user && \
    chown -R qbo_api_user:qbo_api_service /fyle-qbo-api

# Switch to non-root user
USER qbo_api_user

# Expose development port
EXPOSE 8000

# Run development server
CMD /bin/bash run.sh
