# CTFd is built from the checked-in upstream source so qctf can customize the
# Flask application and its plugins without depending on a prebuilt image.
FROM python:3.11-slim-bookworm AS build

WORKDIR /opt/CTFd

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY apps/ctfd/upstream/requirements.txt /opt/CTFd/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/ctfd/upstream/ /opt/CTFd/
COPY plugins/ctfd-headless/qctf_headless /opt/CTFd/CTFd/plugins/qctf_headless
COPY plugins/ctfd-koth/qctf_koth /opt/CTFd/CTFd/plugins/qctf_koth

FROM python:3.11-slim-bookworm AS release

WORKDIR /opt/CTFd

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libffi8 \
        libssl3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --no-log-init --shell /bin/bash -u 1001 ctfd \
    && mkdir -p /var/log/CTFd /var/uploads \
    && chown -R 1001:1001 /var/log/CTFd /var/uploads /opt/CTFd

COPY --from=build /opt/CTFd /opt/CTFd
COPY --from=build /opt/venv /opt/venv
COPY --chown=1001:1001 apps/ctfd/bootstrap.py apps/ctfd/start.sh /opt/qctf/
COPY --chown=1001:1001 tests/plugins /opt/qctf/tests

RUN chown -R 1001:1001 /opt/CTFd /opt/qctf \
    && chmod +x /opt/qctf/start.sh /opt/CTFd/docker-entrypoint.sh

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/opt/CTFd

USER 1001
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/opt/qctf/start.sh"]
