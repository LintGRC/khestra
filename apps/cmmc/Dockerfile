# CMMC SaaS — API (frontend served by Caddy in production)
# Build context: khestra/ (repo root)
FROM python:3.12-slim

WORKDIR /

COPY apps/cmmc/requirements.txt /tmp/cmmc-requirements.txt
# Rewrite local-dev editable paths to their locations inside the image.
RUN sed -i \
    's|-e ../../packages/security_headers|-e /packages/security_headers|' \
    /tmp/cmmc-requirements.txt
COPY packages/ /packages/
RUN pip install --no-cache-dir -r /tmp/cmmc-requirements.txt

COPY apps/cmmc/core/ /apps/cmmc/core/
COPY apps/cmmc/server/ /apps/cmmc/server/
COPY apps/cmmc/assets/ /apps/cmmc/assets/
COPY apps/cmmc/samples/ /apps/cmmc/samples/

# Non-root service user + gosu (privilege drop after volume ownership fix).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /usr/sbin/nologin appuser
COPY deploy/docker/entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint

EXPOSE 8081
VOLUME ["/data"]
ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
CMD ["uvicorn", "main:app", "--app-dir", "apps/cmmc/server", "--host", "0.0.0.0", "--port", "8081"]
