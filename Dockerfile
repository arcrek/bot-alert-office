FROM python:3.11-alpine AS builder

WORKDIR /build

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-alpine

LABEL maintainer="office-bot"
LABEL description="Telegram monitoring bot for Google Sheets"
LABEL version="1.0"

WORKDIR /app

RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    && rm -rf /var/cache/apk/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN addgroup -g 1000 botuser && \
    adduser -D -u 1000 -G botuser botuser

COPY --from=builder /root/.local /home/botuser/.local

COPY bot/ ./bot/

RUN mkdir -p /app/credentials /app/data && \
    chown -R botuser:botuser /app /home/botuser/.local && \
    chmod -R 750 /app

USER botuser

ENV PATH=/home/botuser/.local/bin:$PATH

HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-u", "-m", "bot.main"]
