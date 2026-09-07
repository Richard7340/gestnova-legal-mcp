# gestnova-legal-mcp — imagen del servidor HTTP.
#
# Mismo patron que accounting-mcp y los demas MCPs de la plataforma.
#
# Los `packs` de normativa se copian A PROPOSITO y su ruta se declara con
# LEGAL_PACKS_DIR: instalado con `uv pip install --system .` el codigo vive en
# site-packages, y la resolucion relativa por defecto apuntaria fuera. El
# servidor arrancaria, /health diria ok, y searchLegislation devolveria cero
# normas sin explicar por que.
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PORT=8019 \
    LEGAL_PACKS_DIR=/app/packs

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY src ./src
RUN uv pip install --system .

COPY packs ./packs

EXPOSE 8019
CMD ["gestnova-legal-http"]
