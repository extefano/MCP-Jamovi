# Dockerfile optimizado para entorno Híbrido Python-R (jamovi MCP)
FROM python:3.10-slim

# Evitar prompts durante la instalación
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAMOVI_DATA_ROOT=/data

# 1. Instalar dependencias de sistema para R y sus paquetes estadísticos
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    libxml2-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar paquetes de R críticos para jamovi
# jmv: El motor estadístico
# jmvReadWrite: Para manejar archivos .omv
RUN R -e "install.packages(c('jmv', 'jmvReadWrite', 'jsonlite'), repos='https://cloud.r-project.org/')"

# 3. Configurar entorno Python
WORKDIR /app
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# 4. Copiar código fuente

# 5. Crear punto de montaje para datos (Lectura únicamente según CON-02)
RUN mkdir /data
VOLUME /data

# 6. Exponer puerto si se usa SSE (aunque por defecto es stdio)
EXPOSE 8000

# Comando por defecto para iniciar el servidor MCP
ENTRYPOINT ["python", "-m", "jamovi_mcp"]
