FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      nasm \
      binutils-i686-linux-gnu \
      python3 python3-pip \
      ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Verify i686 linker can generate ELF i386 from NASM object
RUN echo 'global _start\n_start:\n  mov eax, 1\n  xor ebx, ebx\n  int 0x80' > /tmp/test.asm && \
    nasm -f elf32 /tmp/test.asm -o /tmp/test.o && \
    i686-linux-gnu-ld -m elf_i386 /tmp/test.o -o /tmp/test && \
    rm /tmp/test.asm /tmp/test.o /tmp/test

COPY simples-compiler /opt/simples-compiler
RUN cd /opt/simples-compiler && make && cp build/simplesc /usr/local/bin/simplesc && rm -rf /opt/simples-compiler

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY backend/pyproject.toml backend/wsgi.py ./
COPY backend/src/ src/

EXPOSE 5000

CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
