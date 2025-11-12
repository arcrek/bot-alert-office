# Docker Security & Optimization Guide

## Security Improvements Implemented

### 1. Multi-Stage Build
- **Benefit**: Separates build dependencies from runtime, reducing final image size by ~200MB
- **How**: Uses builder stage to compile dependencies, then copies only necessary files to runtime image

### 2. Alpine Linux Base (Primary Dockerfile)
- **Size**: ~50-70MB vs ~150-200MB for Debian slim
- **Security**: Smaller attack surface, fewer vulnerabilities
- **Alternative**: `Dockerfile.debian` available if compatibility issues arise

### 3. Non-Root User
```dockerfile
USER botuser (uid:1000, gid:1000)
```
- Prevents privilege escalation attacks
- Limits damage if container is compromised

### 4. Read-Only Filesystem
```yaml
read_only: true
```
- Container filesystem is immutable
- Only `/tmp` and mounted volumes are writable
- Prevents malware from writing to filesystem

### 5. Dropped Capabilities
```yaml
cap_drop: ALL
```
- Removes all Linux capabilities
- Bot doesn't need any special permissions

### 6. Security Options
```yaml
security_opt:
  - no-new-privileges:true
```
- Prevents privilege escalation via setuid/setgid

### 7. Minimal Dependencies
- Only essential packages installed
- Build dependencies removed after compilation
- No package cache retained

### 8. Isolated Network
- Custom bridge network
- No exposed ports (bot only makes outbound connections)

### 9. Resource Limits (Optional)
Add to `docker-compose.yml` if needed:
```yaml
services:
  telegram-bot:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 128M
```

### 10. Health Checks
- Monitors container health
- Auto-restarts if unhealthy
- Interval: 5 minutes

## Image Size Comparison

| Dockerfile | Base Image | Final Size |
|------------|------------|------------|
| Dockerfile (Alpine) | python:3.11-alpine | ~150MB |
| Dockerfile.debian | python:3.11-slim | ~250MB |
| Without optimization | python:3.11 | ~1GB |

## Security Scanning

### Scan for Vulnerabilities:
```bash
# Using Docker Scout
docker scout cves office-telegram-bot:latest

# Using Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image office-telegram-bot:latest

# Using Snyk
snyk container test office-telegram-bot:latest
```

## Best Practices Applied

### Build Time:
- [x] Multi-stage builds
- [x] Minimal base image
- [x] No unnecessary packages
- [x] Clean package cache
- [x] Specific Python version pinned
- [x] .dockerignore to exclude unnecessary files

### Runtime:
- [x] Non-root user
- [x] Read-only filesystem
- [x] Dropped capabilities
- [x] No new privileges
- [x] Health checks
- [x] Resource limits ready
- [x] Isolated network

### Data:
- [x] Secrets via environment variables
- [x] Credentials mounted read-only
- [x] Data persistence via volumes
- [x] Logs rotation configured

## Usage

### Build Optimized Image:
```bash
# Alpine (smallest, recommended)
docker-compose build

# Debian (if Alpine causes issues)
docker-compose build --build-arg DOCKERFILE=Dockerfile.debian
```

### Run with Security:
```bash
docker-compose up -d
```

### Verify Security:
```bash
# Check running as non-root
docker exec office-telegram-bot whoami
# Output: botuser

# Check read-only filesystem
docker exec office-telegram-bot touch /test
# Output: Read-only file system (expected error)

# Check capabilities
docker inspect office-telegram-bot --format='{{.HostConfig.CapDrop}}'
# Output: [ALL]
```

## Troubleshooting

### Alpine Compatibility Issues
If you encounter issues with Alpine (rare with pure Python projects):

1. Use Debian version:
```bash
docker build -f Dockerfile.debian -t office-telegram-bot .
```

2. Update docker-compose.yml:
```yaml
build:
  dockerfile: Dockerfile.debian
```

### Permission Errors
If volumes have permission issues:
```bash
# Fix ownership
sudo chown -R 1000:1000 ./data ./credentials

# Or adjust user in Dockerfile
RUN adduser -D -u YOUR_USER_ID -G botuser botuser
```

### Read-Only Filesystem Issues
If app needs temporary write access:
```yaml
tmpfs:
  - /tmp:noexec,nosuid,size=10m
  - /app/temp:noexec,nosuid,size=10m  # Add more if needed
```

## Monitoring

### Check Container Health:
```bash
docker ps
# Look for "healthy" status

docker inspect --format='{{.State.Health.Status}}' office-telegram-bot
```

### View Resource Usage:
```bash
docker stats office-telegram-bot
```

### Check for Updates:
```bash
# Update base image
docker pull python:3.11-alpine
docker-compose build --no-cache
docker-compose up -d
```

## Security Checklist

Before deployment:
- [ ] Secrets not hardcoded in Dockerfile
- [ ] .env file not committed to git
- [ ] Credentials file not in image
- [ ] Running as non-root user
- [ ] Unnecessary capabilities dropped
- [ ] Read-only filesystem enabled
- [ ] Health checks configured
- [ ] Logs rotation enabled
- [ ] Image scanned for vulnerabilities
- [ ] Latest base image used

## Additional Hardening (Optional)

### Add AppArmor/SELinux Profile:
```yaml
security_opt:
  - apparmor:docker-default
  - no-new-privileges:true
```

### Add Seccomp Profile:
```yaml
security_opt:
  - seccomp:unconfined  # Or custom profile
```

### Use Docker Content Trust:
```bash
export DOCKER_CONTENT_TRUST=1
docker-compose build
```

## Regular Maintenance

1. **Update base image monthly**:
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Scan for vulnerabilities weekly**:
   ```bash
   docker scout cves office-telegram-bot:latest
   ```

3. **Review logs regularly**:
   ```bash
   docker-compose logs --tail=100
   ```

4. **Backup data**:
   ```bash
   cp -r data/ data.backup/
   ```

## Performance Notes

The optimized image:
- Starts in ~5 seconds
- Uses ~50-100MB RAM idle
- ~150MB disk space (Alpine) vs ~1GB (unoptimized)
- No performance degradation from security measures

## References

- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

