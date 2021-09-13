ARG BASE_IMAGE=python:3.9-slim
FROM $BASE_IMAGE

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG USER_NAME=app
ARG USER_UID=1000
ARG PASSWD=password

RUN useradd -m -s /bin/bash -u $USER_UID $USER_NAME && \
    gpasswd -a $USER_NAME sudo && \
    echo "${USER_NAME}:${PASSWD}" | chpasswd && \
    echo "${USER_NAME} ALL=(ALL) ALL" >> /etc/sudoers

COPY ./pyproject.toml /app/
COPY ./poetry.lock /app/

RUN chown -R ${USER_NAME}:${USER_NAME} /app

WORKDIR /app/

USER $USER_NAME
ENV PATH $PATH:/home/${USER_NAME}/.local/bin
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install poetry --user && \
    poetry config virtualenvs.in-project true && \
    poetry install && \
    rm -rf ~/.cache/pip/* && \
    rm -rf ~/.cache/pypoetry/*

COPY ./main.py /app/
COPY ./custom_logger.py /app/
COPY ./redis_connection.py /app/

ENV PATH=/app/.venv/bin:$PATH

EXPOSE 8000

CMD ["python", "-u", "main.py"]
