# 🚀 Quick Deploy Guide

## The Red Room - 5-Minute Production Deployment

---

## Step 1: Verify (30 seconds)

```bash
pre-production-check.bat
```

**Expected**: All checks pass ✅

---

## Step 2: Configure (1 minute)

```bash
# Copy example
cp .env.example .env

# Edit .env and add your keys
GEMINI_API_KEYS=your_key_1,your_key_2,your_key_3
```

---

## Step 3: Deploy (2 minutes)

### Option A: Docker (Recommended)
```bash
docker build -t redroom:latest .
docker run -d -p 5000:5000 --name redroom redroom:latest
```

### Option B: Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
kubectl get pods -l app=redroom
```

### Option C: Direct
```bash
python web_scanner_app_realtime.py
```

---

## Step 4: Verify (30 seconds)

```bash
# Check health
curl http://localhost:5000/health

# Expected response:
# {"status": "healthy", "service": "redroom-scanner", ...}
```

---

## Step 5: Test (1 minute)

```bash
# Open browser
http://localhost:5000

# Or scan demo app
run.bat fullscan ./demo-app
```

---

## Done! 🎉

Your Red Room is now running in production!

---

## Quick Commands

```bash
# Check status
curl http://localhost:5000/health

# View logs (Docker)
docker logs redroom

# Stop (Docker)
docker stop redroom

# Restart (Docker)
docker restart redroom
```

---

## Troubleshooting

**Health check fails?**
→ Check if service is running: `docker ps`

**Port already in use?**
→ Use different port: `docker run -p 8080:5000 ...`

**Module not found?**
→ Run: `pip install -r requirements-realtime.txt`

---

## Production Checklist

Before going live:
- [ ] Run `pre-production-check.bat` ✅
- [ ] Set up `.env` with your keys
- [ ] Change `SECRET_KEY` in code
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Set up monitoring

---

## Need Help?

- **Full Guide**: [PRODUCTION-READY.md](PRODUCTION-READY.md)
- **Checklist**: [PRE-PRODUCTION-CHECKLIST.md](PRE-PRODUCTION-CHECKLIST.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

---

**The Red Room - Production Ready in 5 Minutes** 🔴
