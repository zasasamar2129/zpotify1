"""MIT License

Copyright (c) 2025 ZACO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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