FROM rocker/r-ver:4.3.3

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAMOVI_DATA_ROOT=/data

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN R -q -e "install.packages(c('jmv', 'jmvReadWrite', 'jsonlite'), repos='https://cloud.r-project.org')"

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src

RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir .

CMD ["python3", "-m", "jamovi_mcp"]
