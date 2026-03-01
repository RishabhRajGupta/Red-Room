# Demo Vulnerable App

This is a deliberately vulnerable Flask app for testing The Red Room.

## Vulnerabilities Included

1. **SQL Injection** at `/api/search`
2. **Race Condition** at `/api/transfer`
3. **XSS** at `/api/comment`

## Test It

```bash
# From the main Red Room directory
python -m redroom.cli fullscan ./demo-app
```

## Expected Results

The Red Room should find all 3 vulnerabilities and generate fixes.

## Manual Testing

```bash
# Run the app
cd demo-app
python app.py

# Test SQL injection
curl "http://localhost:8080/api/search?q=alice' OR '1'='1"

# Test race condition
curl -X POST http://localhost:8080/api/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_id": 1, "to_id": 2, "amount": 100}'

# Test XSS
curl -X POST http://localhost:8080/api/comment \
  -H "Content-Type: application/json" \
  -d '{"comment": "<script>alert(1)</script>"}'
```

## DO NOT use this in production!

This app is intentionally vulnerable for testing purposes only.
