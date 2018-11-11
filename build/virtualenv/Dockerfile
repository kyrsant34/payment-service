FROM python:3.6-alpine3.7 as base
FROM base as builder

RUN mkdir /install
WORKDIR /install

# Add python-libs.txt
COPY python-libs.txt /tmp/

# Install dependencies
RUN apk add --no-cache --virtual .build-deps  \
        build-base \
        libffi-dev \
        mariadb-dev \
    && pip install --install-option="--prefix=/install" -r /tmp/python-libs.txt \
    && apk del .build-deps

FROM base

# Install dependencies
RUN apk add --no-cache \
        bash \
        mariadb-client-libs

COPY --from=builder /install /usr/local

WORKDIR /code/

EXPOSE 8000
