# Safe & Legal Websites for Security Testing 🛡️

## ⚠️ IMPORTANT: Legal Testing Only!

**Never test websites without explicit permission.** Here are completely legal options:

---

## 🎯 Intentionally Vulnerable Applications (100% Legal)

### 1. HTTPBin.org ⭐ RECOMMENDED
```
URL: https://httpbin.org
```
**Why it's safe:**
- Specifically designed for HTTP testing
- Open source and free
- Maintained by Postman
- No vulnerabilities (good for baseline testing)

**Test it:**
```bash
# Via web interface
http://127.0.0.1:5000
Enter: https://httpbin.org

# Via command line
python test_httpbin.py
```

---

### 2. OWASP Juice Shop ⭐ BEST FOR TESTING
```
URL: https://juice-shop.herokuapp.com
```
**Why it's safe:**
- OWASP official project
- Intentionally vulnerable
- Designed for security training
- Contains 100+ vulnerabilities

**What you'll find:**
- SQL Injection ✓
- XSS ✓
- CSRF ✓
- Authentication issues ✓
- Business logic flaws ✓

**Test it:**
```bash
# Via web interface
http://127.0.0.1:5000
Enter: https://juice-shop.herokuapp.com
```

---

### 3. DVWA (Damn Vulnerable Web Application)
```
URL: http://www.dvwa.co.uk (or run locally)
```
**Why it's safe:**
- Specifically designed for penetration testing
- Educational purpose
- Open source

**Run locally:**
```bash
# Docker
docker run --rm -it -p 80:80 vulnerables/web-dvwa

# Then test
http://127.0.0.1:5000
Enter: http://localhost
```

---

### 4. WebGoat
```
URL: Run locally (OWASP project)
```
**Why it's safe:**
- OWASP official training platform
- Intentionally insecure
- Educational lessons included

**Run locally:**
```bash
# Download from OWASP
# https://owasp.org/www-project-webgoat/

# Then test
http://127.0.0.1:5000
Enter: http://localhost:8080/WebGoat
```

---

### 5. HackTheBox (Retired Machines)
```
URL: https://www.hackthebox.com
```
**Why it's safe:**
- Legal penetration testing platform
- Retired machines are free
- Designed for security training

**Note:** Requires account signup

---

### 6. TryHackMe
```
URL: https://tryhackme.com
```
**Why it's safe:**
- Legal security training platform
- Practice rooms available
- Educational purpose

**Note:** Requires account signup

---

### 7. PentesterLab
```
URL: https://pentesterlab.com
```
**Why it's safe:**
- Legal penetration testing exercises
- Some free exercises available
- Educational platform

---

### 8. PortSwigger Web Security Academy
```
URL: https://portswigger.net/web-security
```
**Why it's safe:**
- Created by Burp Suite makers
- Free labs available
- Designed for testing

---

## 🏠 Run Your Own Vulnerable Apps Locally

### Option 1: Docker Compose
```bash
# Create docker-compose.yml
version: '3'
services:
  dvwa:
    image: vulnerables/web-dvwa
    ports:
      - "80:80"
  
  juice-shop:
    image: bkimminich/juice-shop
    ports:
      - "3000:3000"
  
  webgoat:
    image: webgoat/goatandwolf
    ports:
      - "8080:8080"
```

```bash
# Start all vulnerable apps
docker-compose up -d

# Test them
http://127.0.0.1:5000
Enter: http://localhost
```

### Option 2: Virtual Machines
- Download vulnerable VMs from VulnHub
- Run in VirtualBox/VMware
- Test in isolated environment

---

## 📋 Quick Test Checklist

### ✅ Before Testing:
- [ ] Confirm site is designed for security testing
- [ ] Read the site's terms of service
- [ ] Use a test environment (not production)
- [ ] Document your testing
- [ ] Follow responsible disclosure

### ✅ Safe Sites to Test:
- [ ] HTTPBin.org (baseline testing)
- [ ] Juice Shop (comprehensive testing)
- [ ] DVWA (classic vulnerabilities)
- [ ] WebGoat (educational)
- [ ] Your own local applications
- [ ] Docker containers on localhost

### ❌ Never Test:
- [ ] Production websites without permission
- [ ] Government websites
- [ ] Banking/financial sites
- [ ] Healthcare sites
- [ ] Any site you don't own without written permission

---

## 🚀 Recommended Testing Workflow

### Step 1: Start with HTTPBin
```bash
# Test your scanner works
http://127.0.0.1:5000
Enter: https://httpbin.org
```
**Expected:** Clean scan, no vulnerabilities (good baseline)

### Step 2: Test on Juice Shop
```bash
# Test vulnerability detection
http://127.0.0.1:5000
Enter: https://juice-shop.herokuapp.com
```
**Expected:** Multiple vulnerabilities found

### Step 3: Test on DVWA (Local)
```bash
# Test all 70 tests
docker run -p 80:80 vulnerables/web-dvwa

http://127.0.0.1:5000
Enter: http://localhost
```
**Expected:** Many vulnerabilities (SQL injection, XSS, etc.)

### Step 4: Test Your Own Apps
```bash
# Test your development projects
http://127.0.0.1:5000
Enter: http://localhost:8000
```
**Expected:** Find and fix real issues

---

## 📊 What to Expect from Each Site

### HTTPBin.org
- **Endpoints Found:** 20-30
- **Vulnerabilities:** 0-2 (mostly missing headers)
- **Scan Time:** 1-2 minutes
- **Purpose:** Baseline testing

### Juice Shop
- **Endpoints Found:** 50-100
- **Vulnerabilities:** 10-30
- **Scan Time:** 3-5 minutes
- **Purpose:** Comprehensive testing

### DVWA
- **Endpoints Found:** 10-20
- **Vulnerabilities:** 15-25
- **Scan Time:** 2-3 minutes
- **Purpose:** Classic vulnerability testing

---

## 🎓 Educational Resources

### Learn More About:
1. **OWASP Top 10**: https://owasp.org/www-project-top-ten/
2. **Web Security**: https://portswigger.net/web-security
3. **Ethical Hacking**: https://www.hackthebox.com
4. **Bug Bounty**: https://www.bugcrowd.com/hackers/

### Practice Platforms:
- HackTheBox
- TryHackMe
- PentesterLab
- HackerOne (bug bounty)
- Bugcrowd (bug bounty)

---

## ⚖️ Legal Disclaimer

### You Are Responsible For:
- Obtaining proper authorization
- Following laws in your jurisdiction
- Respecting terms of service
- Ethical behavior
- Responsible disclosure

### This Tool Is For:
- ✅ Educational purposes
- ✅ Testing your own applications
- ✅ Authorized penetration testing
- ✅ Security research with permission

### This Tool Is NOT For:
- ❌ Unauthorized access
- ❌ Malicious activities
- ❌ Breaking laws
- ❌ Harming others

---

## 🎯 Quick Start Commands

### Test HTTPBin (Safest)
```bash
python test_httpbin.py
```

### Test via Web Interface
```bash
# Start server
python web_scanner_app.py

# Open browser
http://127.0.0.1:5000

# Enter URL
https://httpbin.org
```

### Test Juice Shop
```bash
# Via web interface
http://127.0.0.1:5000
Enter: https://juice-shop.herokuapp.com
```

### Test Local DVWA
```bash
# Start DVWA
docker run -p 80:80 vulnerables/web-dvwa

# Test it
http://127.0.0.1:5000
Enter: http://localhost
```

---

## 📝 Report Template

After testing, document your findings:

```
SECURITY SCAN REPORT
====================

Target: [URL]
Date: [Date]
Scanner: The Red Room v1.0
Tests: 70 vulnerability checks

SUMMARY
-------
Endpoints Found: [X]
Vulnerabilities: [X]
Critical: [X]
High: [X]
Medium: [X]
Low: [X]

FINDINGS
--------
[List vulnerabilities]

RECOMMENDATIONS
---------------
[List fixes]
```

---

## 🎉 You're Ready!

**Recommended first test:**
```bash
python test_httpbin.py
```

Or use the web interface:
```
http://127.0.0.1:5000
Enter: https://httpbin.org
```

**Happy (legal) hacking!** 🔴🛡️

---

## 📞 Need Help?

- Check documentation: `WEB-SCANNER-README.md`
- Review test results: `httpbin-test-report.txt`
- Read implementation: `70-TESTS-COMPLETE.md`

**Remember: Always test legally and ethically!** ⚖️
