# Docker Hub Deployment Guide

## Push Image to Docker Hub

### 1. Build the image with your Docker Hub username

```bash
docker build -t nguyendangdat/bot-alert-office:latest .
```

### 2. Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

### 3. Push the image

```bash
docker push nguyendangdat/bot-alert-office:latest
```

### 4. (Optional) Tag with version

```bash
docker tag nguyendangdat/bot-alert-office:latest nguyendangdat/bot-alert-office:v1.0.0
docker push nguyendangdat/bot-alert-office:v1.0.0
```

## Deploy from Docker Hub

### Quick Start

1. **Ensure you have the required files:**
   - `docker-compose.hub.yml`
   - `.env` (with your configuration)
   - `credentials/google_credentials.json`

2. **Start the bot:**

```bash
docker-compose -f docker-compose.hub.yml up -d
```

### Commands

```bash
# Start the bot
docker-compose -f docker-compose.hub.yml up -d

# View logs
docker-compose -f docker-compose.hub.yml logs -f

# Stop the bot
docker-compose -f docker-compose.hub.yml down

# Update to latest image
docker-compose -f docker-compose.hub.yml pull
docker-compose -f docker-compose.hub.yml up -d

# Restart the bot
docker-compose -f docker-compose.hub.yml restart
```

### Environment Setup

Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_SHEET_NAME=SLOT OFFICE TRIAL
GOOGLE_CREDENTIALS_PATH=./credentials/google_credentials.json
TIMEZONE=Asia/Bangkok
CHECK_INTERVAL_MINUTES=15
```

## Advantages of Using Docker Hub Image

✅ No need to build locally (faster deployment)  
✅ Consistent image across all environments  
✅ Easy updates with `docker-compose pull`  
✅ Ideal for production deployments  
✅ Works on any platform (Windows, Linux, macOS)

## Multi-Architecture Support

If you want to support multiple platforms (amd64, arm64):

```bash
# Create and use buildx builder
docker buildx create --name multiarch --use

# Build and push for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t nguyendangdat/bot-alert-office:latest \
  --push .
```

## Security Note

The Docker Hub image uses the same security features:
- Non-root user (botuser)
- Read-only filesystem
- Dropped capabilities
- No new privileges
- Limited tmpfs

See `DOCKER_SECURITY.md` for details.

