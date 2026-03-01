# 🔒 Removing API Keys from Git History

## ⚠️ CRITICAL: API Keys Found in Git History

The commit "Stable Version" (f068972) contains real API keys that need to be removed from git history.

---

## What We're Doing

1. Create backup branch (safety)
2. Rewrite git history to remove the problematic commit
3. Force push clean history to GitHub
4. Revoke exposed API keys (IMPORTANT!)

---

## Step-by-Step Execution

### Step 1: Create Backup (Safety First)
```bash
git branch backup-before-rewrite
```

### Step 2: Rebase to Remove Commit
```bash
# Interactive rebase to remove the "Stable Version" commit
git rebase -i f068972^
```

In the editor that opens:
- Find the line with "Stable Version"
- Change "pick" to "drop"
- Save and close

### Step 3: Verify History is Clean
```bash
# Check the commit is gone
git log --oneline

# Verify no API keys in history
git log -p | grep -i "AIzaSy"
```

### Step 4: Force Push to GitHub
```bash
# Force push the rewritten history
git push origin main --force
```

---

## ⚠️ IMPORTANT: Revoke Exposed API Keys

The API keys were exposed in git history. You MUST revoke them:

### Gemini API Keys:
1. Visit: https://makersuite.google.com/app/apikey
2. Find these keys and delete them:
   - AIzaSyBkjQf8hUqT_qTx2cilgpuaExdviEBa-0g
   - AIzaSyBqZ6jeAg-NF6v6FH-KWqsNW2bnlhuxfNU
   - AIzaSyDt6Uf1-fgnUmgx6rUIHi_R3CsXlOh6sM8
   - AIzaSyBsMwNoGgslF97gETtHYtc5u3NFPCAFuCI
   - AIzaSyCG2MddLWVIdHjOH7FTSNJxEwu8DR0HZoE
   - AIzaSyDPNItnbRl7AwqcrGVMAwANFpmVvzIwKJA
   - AIzaSyCDrN5jpl-AXKsSd_ovf8CE_rvzVCf7aJA
   - AIzaSyB5kEinx4DgvzBRqmnQr5Dofh6y7MgapZk
3. Generate new keys
4. Update your local `.env` file

---

## Alternative: Start Fresh Repository

If you prefer a clean start:

```bash
# 1. Remove git history
rm -rf .git

# 2. Initialize new repo
git init

# 3. Add all files
git add .

# 4. Create initial commit
git commit -m "Initial commit - Production ready"

# 5. Add remote
git remote add origin <your-github-url>

# 6. Force push
git push origin main --force
```

---

## Verification Checklist

After cleanup:
- [ ] No "Stable Version" commit in history
- [ ] No API keys in git log
- [ ] `.env.example` has placeholders only
- [ ] Old API keys revoked
- [ ] New API keys generated
- [ ] Local `.env` updated with new keys

---

## Recovery (If Something Goes Wrong)

If you need to restore:
```bash
git checkout backup-before-rewrite
git branch -D main
git checkout -b main
```

---

**CRITICAL**: Revoke the exposed API keys immediately after pushing!
