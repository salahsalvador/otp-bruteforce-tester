# OTP Brute-force Tester

A multithreaded OTP brute-force testing tool built for authorized penetration testing engagements.

## Features
- Multithreaded with configurable concurrency
- Configurable OTP range, batch size, and delay
- Handles rate-limiting (429) and bad requests (400)
- Stops automatically on success

## Requirements
pip install requests

## Usage
python otp_bruteforce.py \
  --url https://target.com/api/endpoint \
  --mobile 0600000000 \
  --password YourPassword \
  --start 0 \
  --end 999999 \
  --workers 60 \
  --batch-size 200 \
  --delay 0.05

## Arguments
| Argument | Description |
|----------|-------------|
| --url | Target API endpoint |
| --mobile | Mobile number |
| --password | Account password |
| --start | OTP start range (default: 0) |
| --end | OTP end range (default: 999999) |
| --workers | Concurrent threads (default: 60) |
| --batch-size | OTPs per batch (default: 200) |
| --delay | Delay between batches in seconds (default: 0.05) |

## Real-World Use Case

During a web application penetration test, a **password reset flow** was identified
that lacked OTP brute-force protection.

### Vulnerability
The `/confirm_forgot_password` endpoint accepted unlimited OTP attempts
with no rate limiting or lockout mechanism, allowing an attacker to
brute-force the 6-digit OTP (1,000,000 possible combinations).

### Testing Methodology
1. Triggered a password reset for a test account
2. Used this script to brute-force the OTP range
3. Successfully reset the password, confirming the vulnerability

### Impact
- Account takeover of any user whose phone number is known
- No rate limiting or lockout was in place

### Remediation Recommended
- Implement rate limiting on OTP endpoints
- Lock account after N failed attempts
- Set short OTP expiry time (e.g. 2 minutes)
- Implement CAPTCHA after repeated failures

## ⚠️ Disclaimer
This tool is intended for **authorized penetration testing only**.
Do not use against any system without explicit written permission.
The author is not responsible for any misuse.
