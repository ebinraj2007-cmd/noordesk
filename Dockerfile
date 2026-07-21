# NoorDesk — production image
#
# Multi-stage. The first stage has a compiler and build headers; the second has
# neither. Anything present in the final image is attack surface, so the build
# toolchain doesn't travel with it.
#
# Two decisions worth naming, because they're the ones that get skipped:
#
#   * The app runs as a non-root user. If someone finds an RCE in a dependency,
#     the difference between `noordesk` and `root` inside the container is the
#     difference between an annoyance and a container escape being worth trying.
#
#   * The healthcheck hits the /healthz endpoint the app already exposes, which
#     touches storage. A process that is running but can't reach its database is
#     not healthy, and a liveness probe that only checks "is the port open"
#     would call it healthy anyway.

# ---------------------------------------------------------------- builder ---
FROM python:3.12-slim-bookworm AS builder

# Build wheels into a venv we can copy wholesale. Copying a venv is simpler and
# more predictable than --user installs or replaying pip in the runtime stage.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# requirements.txt is copied on its own, before the source. Docker caches layers,
# and dependencies change far less often than code — so an ordinary code change
# reuses this layer instead of reinstalling everything.
WORKDIR /app
COPY requirements.txt .

# lingua ships wheels, but pin build deps here anyway so a source build of any
# transitive dependency doesn't fail on a machine without a compiler.
RUN apt-get update \
 && apt-get install --no-install-recommends -y build-essential \
 && pip install --upgrade pip \
 && pip install -r requirements.txt \
 && apt-get purge -y build-essential \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------- runtime ---
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    NOORDESK_DB=/data/noordesk.db \
    NOORDESK_PROFILE=/data/profile.json

# curl is for the healthcheck. It is the one thing we add, and it's ~2MB.
RUN apt-get update \
 && apt-get install --no-install-recommends -y curl \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1001 noordesk \
 && useradd --system --uid 1001 --gid noordesk --create-home noordesk

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=noordesk:noordesk . .

# SQLite lives on a volume, not in the image layer. A container is disposable;
# the operator's customer messages are not.
RUN mkdir -p /data && chown noordesk:noordesk /data
VOLUME ["/data"]

USER noordesk

EXPOSE 8000

# /healthz opens the database. "The port answers" is not the same as "the app
# works", and this is the difference.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl --fail --silent http://127.0.0.1:8000/healthz || exit 1

# 0.0.0.0 inside the container is correct — the container's network namespace is
# the boundary, and you publish the port deliberately with -p. Binding 127.0.0.1
# here would make the app unreachable from outside the container.
#
# uvicorn[standard] is in requirements.txt, which is what gives us WebSocket
# support. Without it the dashboard silently falls back to polling.
CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
