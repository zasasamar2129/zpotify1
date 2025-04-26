from mbot import Mbot
from os import sys, mkdir, path
import subprocess
import signal
import os
import time
from typing import Optional

bot_process: Optional[subprocess.Popen] = None

def terminate_processes():
    global bot_process
    if bot_process:
        try:
            # Redirect output to devnull to prevent lingering logs
            bot_process.stdout = subprocess.DEVNULL
            bot_process.stderr = subprocess.DEVNULL
            
            # Send termination signal to process group
            pgid = os.getpgid(bot_process.pid)
            os.killpg(pgid, signal.SIGTERM)
            
            # Wait with timeout
            for _ in range(5):  # 5 second timeout
                if bot_process.poll() is not None:
                    break
                time.sleep(1)
            else:
                os.killpg(pgid, signal.SIGKILL)
                
        except Exception as e:
            print(f"Termination error: {e}", file=sys.stderr)
        finally:
            bot_process = None
            sys.stdout.flush()  # Ensure all output is flushed

def signal_handler(sig, frame):
    terminate_processes()
    # Clear the terminal
    os.system('clear' if os.name == 'posix' else 'cls')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not path.exists("cache"):
        mkdir("cache")
    
    try:
        # Start bot.py with output redirection
        bot_process = subprocess.Popen(
            ["python3", "mbot/pirate/bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            text=True
        )
        
        # Run main bot
        Mbot().run()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        terminate_processes()
        # Clear terminal on exit
        os.system('clear' if os.name == 'posix' else 'cls')