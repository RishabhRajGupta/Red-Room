# 🐳 Docker Setup Guide

## Installing Docker on Windows

Docker is required for the `fullscan` feature to deploy and test applications in isolated containers.

---

## Quick Install (Recommended)

### Option 1: Docker Desktop (Easiest)

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"
   - File size: ~500MB

2. **Install**
   ```
   - Run the installer (Docker Desktop Installer.exe)
   - Follow the installation wizard
   - Enable WSL 2 if prompted (recommended)
   - Restart your computer when prompted
   ```

3. **Verify Installation**
   ```bash
   docker --version
   # Expected: Docker version 24.x.x or higher
   
   docker run hello-world
   # Expected: "Hello from Docker!" message
   ```

4. **Start Docker Desktop**
   - Docker Desktop should start automatically
   - Look for Docker icon in system tray
   - Wait for "Docker Desktop is running" status

---

## System Requirements

### Minimum:
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- OR Windows 11 64-bit
- 4GB RAM (8GB recommended)
- BIOS-level hardware virtualization support enabled

### Check Your Windows Version:
```bash
winver
# Should show Windows 10 Build 19041+ or Windows 11
```

---

## Alternative: Docker without Docker Desktop

If you can't use Docker Desktop (licensing, system requirements, etc.):

### Option 2: Rancher Desktop (Free, Open Source)

1. **Download**
   - Visit: https://rancherdesktop.io/
   - Click "Download for Windows"

2. **Install**
   - Run installer
   - Choose "dockerd (moby)" as container runtime
   - Restart when prompted

3. **Verify**
   ```bash
   docker --version
   ```

### Option 3: Podman Desktop (Docker Alternative)

1. **Download**
   - Visit: https://podman-desktop.io/
   - Click "Download for Windows"

2. **Install and Configure**
   - Run installer
   - Podman is Docker-compatible

3. **Use with Red Room**
   ```bash
   # Podman uses same commands as Docker
   podman --version
   ```

---

## Configuration for Red Room

### 1. Increase Resources (Optional but Recommended)

**Docker Desktop Settings:**
- Open Docker Desktop
- Go to Settings → Resources
- Adjust:
  - **CPUs**: 4+ (more is better)
  - **Memory**: 4GB+ (8GB recommended)
  - **Disk**: 20GB+

### 2. Enable WSL 2 (Recommended)

WSL 2 provides better performance:

```bash
# Check WSL version
wsl --list --verbose

# If not WSL 2, upgrade:
wsl --set-default-version 2
```

### 3. Test Docker Works

```bash
# Test basic functionality
docker run hello-world

# Test with a real container
docker run -d -p 8080:80 nginx
# Visit http://localhost:8080 in browser
# Should see "Welcome to nginx!"

# Clean up
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
```

---

## Using Docker with Red Room

### Once Docker is Installed:

1. **Test Full Scan**
   ```bash
   run.bat fullscan ./demo-app
   ```

2. **What Happens:**
   - Red Room builds a Docker image from your app
   - Deploys it in an isolated container
   - Runs 70 security tests
   - Analyzes results with AI agents
   - Generates fixes

3. **Expected Output:**
   ```
   Deployment:
     Status: Success
     Container: redroom-target-xxxxx
     URL: http://localhost:8080
   
   Scanning:
     Tests: 70/70 complete
     Vulnerabilities: X found
   
   Analysis:
     Agent I: Hypotheses generated
     Agent II: Exploits confirmed
     Agent III: Patches created
   ```

---

## Troubleshooting

### "Docker daemon is not running"

**Solution:**
1. Start Docker Desktop from Start Menu
2. Wait for "Docker Desktop is running" in system tray
3. Try command again

### "WSL 2 installation is incomplete"

**Solution:**
```bash
# Install WSL 2 kernel update
# Download from: https://aka.ms/wsl2kernel
# Run the installer
# Restart Docker Desktop
```

### "Hardware virtualization is not enabled"

**Solution:**
1. Restart computer
2. Enter BIOS/UEFI (usually F2, F10, or Del during boot)
3. Find "Virtualization Technology" or "VT-x" or "AMD-V"
4. Enable it
5. Save and exit
6. Install Docker Desktop again

### "docker: command not found" after installation

**Solution:**
```bash
# Close and reopen PowerShell/Terminal
# Or restart computer
# Docker Desktop adds to PATH automatically
```

### "Port already in use"

**Solution:**
```bash
# Use different port
run.bat fullscan ./demo-app --port 8081

# Or find what's using the port
netstat -ano | findstr :8080

# Kill the process
taskkill /PID <process_id> /F
```

---

## Without Docker (Alternative)

If you can't install Docker, you can still use Red Room:

### 1. Web Scanner (No Docker Required)
```bash
# Start web scanner
python web_scanner_app_realtime.py

# Visit http://localhost:5000
# Scan any website you own
```

### 2. Three-Agent System (No Docker Required)
```bash
# Test the AI agents
python test_three_agents.py

# Analyze git diffs
run.bat agents --diff-file changes.diff
```

### 3. Manual Testing
```bash
# Run your app manually
cd demo-app
python app.py

# In another terminal, scan it
run.bat scan http://localhost:8080
```

---

## Docker Commands Reference

### Useful Commands:

```bash
# Check Docker status
docker info

# List running containers
docker ps

# List all containers
docker ps -a

# Stop all containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# View logs
docker logs <container_id>

# Clean up everything
docker system prune -a
```

---

## Performance Tips

### 1. Use WSL 2 Backend
- Faster than Hyper-V
- Better file system performance
- Lower resource usage

### 2. Allocate Enough Resources
- Minimum: 2 CPUs, 4GB RAM
- Recommended: 4 CPUs, 8GB RAM
- For heavy scanning: 8 CPUs, 16GB RAM

### 3. Use Docker BuildKit
```bash
# Enable BuildKit for faster builds
set DOCKER_BUILDKIT=1
```

### 4. Clean Up Regularly
```bash
# Remove unused containers, images, networks
docker system prune -a
```

---

## Security Considerations

### 1. Docker Desktop Licensing
- Free for personal use, education, small businesses
- Requires license for large enterprises
- Check: https://www.docker.com/pricing/

### 2. Container Security
- Red Room uses isolated containers
- Each scan runs in fresh container
- Containers are destroyed after scan
- No data persists between scans

### 3. Network Isolation
- Containers run on isolated network
- Only exposed ports are accessible
- No access to host filesystem by default

---

## Quick Start After Installation

```bash
# 1. Verify Docker works
docker --version
docker run hello-world

# 2. Test with Red Room
run.bat fullscan ./demo-app

# 3. Check results
# Scan report will be generated
# Vulnerabilities will be listed
# Fixes will be suggested
```

---

## Summary

### To Use Full Scan Feature:

1. ✅ Install Docker Desktop (or alternative)
2. ✅ Start Docker Desktop
3. ✅ Verify: `docker --version`
4. ✅ Run: `run.bat fullscan ./demo-app`

### Without Docker:

1. ✅ Use web scanner: `python web_scanner_app_realtime.py`
2. ✅ Use three-agent test: `python test_three_agents.py`
3. ✅ Manual testing with your own server

---

## Need Help?

### Docker Issues:
- Docker Desktop Docs: https://docs.docker.com/desktop/
- Docker Forums: https://forums.docker.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/docker

### Red Room Issues:
- Check: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Run: `pre-production-check.bat`
- Test: `python test_three_agents.py`

---

**Docker is optional but recommended for the full scanning experience!**

The web scanner and three-agent system work perfectly without Docker.
