ARG VIRTUALENV_IMAGE
FROM ${VIRTUALENV_IMAGE}

COPY . /code

ENTRYPOINT ["/code/build/release/docker-entrypoint.sh"]
