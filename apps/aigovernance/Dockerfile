# AI Governance — API
# Build context: khestra/ (repo root)
FROM python:3.12-slim

WORKDIR /

COPY apps/aigovernance/requirements.txt /tmp/aigov-requirements.txt
RUN sed -i \
    's|-e ../../packages/security_headers|-e /packages/security_headers|' \
    /tmp/aigov-requirements.txt
COPY packages/ /packages/
RUN pip install --no-cache-dir -r /tmp/aigov-requirements.txt

COPY apps/aigovernance/server/ /apps/aigovernance/server/
COPY apps/aigovernance/core/ /apps/aigovernance/core/

# Non-root service user + gosu (privilege drop after volume ownership fix).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /usr/sbin/nologin appuser
COPY deploy/docker/entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint

EXPOSE 8083
VOLUME ["/apps/aigovernance/data"]
ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
CMD ["uvicorn", "main:app", "--app-dir", "apps/aigovernance/server", "--host", "0.0.0.0", "--port", "8083"]
