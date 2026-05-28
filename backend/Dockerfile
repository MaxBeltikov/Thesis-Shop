FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2/reportlab fonts and common builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    fontconfig \
    fonts-dejavu-core \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend project
COPY backend /app/backend
WORKDIR /app/backend

EXPOSE 8000

# Default: run migrations + demo data (idempotent) then dev server
CMD ["sh", "-lc", "python manage.py migrate && python manage.py load_demo && python manage.py runserver 0.0.0.0:8000"]
