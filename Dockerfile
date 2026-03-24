# ---- Stage 1: Build frontend assets ----
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Stage 2: Python Application ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app/
# Bring the compiled CSS & JS from the builder stage
COPY --from=frontend-builder /app/static/css /app/static/css/
COPY --from=frontend-builder /app/static/js /app/static/js/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
