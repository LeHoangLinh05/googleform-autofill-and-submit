import argparse
import datetime
import json
import random
import time
import requests

import form

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    # thêm user agents hợp lý khác nếu muốn
]

def fill_random_value(type_id, entry_id, options, required = False, entry_name = ''):
    ''' Fill random value for a form entry 
        Customize your own fill_algorithm here
        Note: please follow this func signature to use as fill_algorithm in form.get_form_submit_request '''
    # Customize for specific entry_id
    if entry_id == 'emailAddress':
        return f"test{random.randint(1000,9999)}@gmail.com"
    if entry_name == "Short answer":
        return 'Random answer!'
    # Random value for each type
    if type_id in [0, 1]: # Short answer and Paragraph
        return '' if not required else 'Ok!'
    if type_id == 2: # Multiple choice
        return random.choice(options)
    if type_id == 3: # Dropdown
        return random.choice(options)
    if type_id == 4: # Checkboxes
        return random.sample(options, k=random.randint(1, len(options)))
    if type_id == 5: # Linear scale
        return random.choice(options)
    if type_id == 7: # Grid choice
        return random.choice(options)
    if type_id == 9: # Date
        return datetime.date.today().strftime('%Y-%m-%d')
    if type_id == 10: # Time
        return datetime.datetime.now().strftime('%H:%M')
    return ''

def generate_request_body(url: str, only_required = False):
    ''' Generate random request body data '''
    data = form.get_form_submit_request(
        url,
        only_required = only_required,
        fill_algorithm = fill_random_value,
        output = "return",
        with_comment = False
    )
    data = json.loads(data)
    # you can also override some values here
    return data

def submit(url: str, data: dict, max_retries=4):
    url = form.get_form_response_url(url)
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": url.replace('/formResponse', '/viewform'),
        "Origin": "https://docs.google.com",
        # thêm header nếu cần
    }
    print("Submitting to", url)
    print("Data:", data, flush=True)

    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.post(url, data=data, headers=headers, timeout=10)
            print(f"Attempt {attempt}: status {res.status_code}")
            # nếu Google trả về 200, coi như ok (vẫn cần kiểm tra response text nếu muốn)
            if res.status_code == 200:
                return res
            # nếu rate limited, chờ theo lộ trình backoff
            if res.status_code in (429, 500, 502, 503, 504):
                sleep_time = backoff + random.uniform(0, 1.0)  # jitter
                print(f"Got {res.status_code}, sleeping {sleep_time:.1f}s before retry")
                time.sleep(sleep_time)
                backoff *= 2
                continue
            # các mã khác: in log và dừng (không retry vô tận)
            print("Unexpected response, not retrying. Response text (start):", res.text[:200])
            return res
        except requests.RequestException as e:
            sleep_time = backoff + random.uniform(0, 1.0)
            print(f"RequestException: {e}, sleeping {sleep_time:.1f}s before retry")
            time.sleep(sleep_time)
            backoff *= 2
    print("Max retries reached, aborting.")
    return None
def main(url, only_required = False):
    try:
        payload = generate_request_body(url, only_required = only_required)
        submit(url, payload)
        print("Done!!!")
    except Exception as e:
        print("Error!", e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit google form with custom data')
    parser.add_argument('url', help='Google Form URL')
    parser.add_argument('-r', '--required', action='store_true', help='Only include required fields')
    args = parser.parse_args()
    main(args.url, args.required)
