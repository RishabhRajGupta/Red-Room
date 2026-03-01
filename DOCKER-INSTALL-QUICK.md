# 🐳 Docker Quick Install

## 3-Step Docker Setup for Windows

---

## Step 1: Download (2 minutes)

Visit: **https://www.docker.com/products/docker-desktop**

Click: **"Download for Windows"**

File size: ~500MB

---

## Step 2: Install (5 minutes)

1. Run `Docker Desktop Installer.exe`
2. Click "OK" to enable WSL 2 (recommended)
3. Click "Install"
4. Wait for installation
5. Click "Close and restart"
6. **Restart your computer**

---

## Step 3: Verify (1 minute)

Open PowerShell and run:

```bash
docker --version
```

Expected output:
```
Docker version 24.x.x, build xxxxx
```

Test it works:
```bash
docker run hello-world
```

Expected output:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## ✅ Done!

Now you can use the full scan feature:

```bash
run.bat fullscan ./demo-app
```

---

## Troubleshooting

### "docker: command not found"
→ Close and reopen PowerShell
→ Or restart computer

### "Docker Desktop is not running"
→ Start Docker Desktop from Start Menu
→ Wait for "Docker Desktop is running" in system tray

### "WSL 2 installation incomplete"
→ Download: https://aka.ms/wsl2kernel
→ Install and restart Docker Desktop

---

## System Requirements

- Windows 10 64-bit (Build 19041+) or Windows 11
- 4GB RAM minimum (8GB recommended)
- Virtualization enabled in BIOS

Check Windows version:
```bash
winver
```

---

## Alternative: Without Docker

You can still use Red Room without Docker:

```bash
# Web scanner (no Docker needed)
python web_scanner_app_realtime.py

# Three-agent test (no Docker needed)
python test_three_agents.py
```

See [WHAT-WORKS-NOW.md](WHAT-WORKS-NOW.md) for details.

---

**Need detailed help?** See [DOCKER-SETUP.md](DOCKER-SETUP.md)
