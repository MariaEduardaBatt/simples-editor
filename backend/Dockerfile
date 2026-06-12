FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      nasm \
      binutils-i686-linux-gnu \
      python3 python3-pip \
      ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY simples-compiler /opt/simples-compiler
RUN cd /opt/simples-compiler && make && cp build/simplesc /usr/local/bin/simplesc && rm -rf /opt/simples-compiler

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY backend/pyproject.toml backend/wsgi.py ./
COPY backend/src/ src/

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "wsgi:app"]
