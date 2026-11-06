# syntax=docker/dockerfile:1
FROM python:3.13-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 AUDIT_LOG=/var/lib/gateway/audit.jsonl USERS_FILE=/run/config/users.json
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --no-create-home app \
    && mkdir -p /var/lib/gateway && chown app:app /var/lib/gateway
COPY --from=build /install /usr/local
# The runtime image needs no package manager: remove pip, setuptools and wheel (including the copies bundled with
# ensurepip), which also removes their vendored libraries flagged by the Trivy image scan.
RUN python -m pip uninstall -y pip setuptools wheel; \
    rm -rf /usr/local/lib/python3.13/ensurepip/_bundled /usr/local/lib/python3.13/site-packages/pip*; \
    find / -xdev \( -name "setuptools*" -o -name "msgpack*" -o -name "urllib3*" \) -path "*site-packages*" -prune -print 2>/dev/null; true
WORKDIR /app
COPY --chown=root:root app ./app
COPY --chown=root:root data/docs ./data/docs
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
