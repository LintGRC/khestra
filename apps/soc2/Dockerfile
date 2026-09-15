# SOC 2 — API (frontend served by Caddy in production)
# Build context: khestra/ (repo root)
FROM python:3.12-slim

WORKDIR /

COPY apps/soc2/requirements.txt /tmp/soc2-requirements.txt
RUN sed -i \
    's|-e ../../packages/security_headers|-e /packages/security_headers|' \
    /tmp/soc2-requirements.txt
COPY packages/ /packages/
RUN pip install --no-cache-dir -r /tmp/soc2-requirements.txt

COPY apps/soc2/server/ /apps/soc2/server/
COPY apps/soc2/core/ /apps/soc2/core/
COPY apps/cmmc/core/ /apps/cmmc/core/

# Non-root service user + gosu (privilege drop after volume ownership fix).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /usr/sbin/nologin appuser
COPY deploy/docker/entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint

EXPOSE 8082
VOLUME ["/apps/soc2/soc2_data"]
ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
CMD ["uvicorn", "main:app", "--app-dir", "apps/soc2/server", "--host", "0.0.0.0", "--port", "8082"]
