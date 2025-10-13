import time
import random
import signal
import sys
from main import main


STOP = False

def handle_sigint(sig, frame):
    global STOP
    STOP = True
    print("Received stop signal, will exit after current iteration...")

signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTERM, handle_sigint)

def run_loop(url, only_required=True, min_delay=10, max_delay=40, max_runs=None):
    run_count = 0
    while not STOP:
        try:
            print(f"=== Run #{run_count+1} ===")
            main(url, only_required=only_required)
        except Exception as e:
            print("Error in main loop:", e)
        run_count += 1
        if max_runs and run_count >= max_runs:
            print("Reached max_runs, exiting.")
            break
        delay = random.uniform(min_delay, max_delay)
        print(f"Sleeping {delay:.1f}s before next submit.")
        # sleep in small chunks so SIGINT can be handled quicker
        slept = 0.0
        while slept < delay and not STOP:
            time.sleep(min(1.0, delay - slept))
            slept += min(1.0, delay - slept)
    print("Loop stopped. Exiting.")

if __name__ == '__main__':
    url = "https://docs.google.com/forms/d/e/1FAIpQLSf9gNO4XGdbHaPaziJKFpaJtv3XrAUVrRsZaDjowmu1takmIg/viewform"
    run_loop(url, only_required=True, min_delay=15, max_delay=40, max_runs=None)
