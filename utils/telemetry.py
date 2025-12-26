
import os
import platform
import socket
import threading
import uuid
import urllib.request
import urllib.parse
from flask import current_app

TELEMETRY_MARKER_FILE = ".telemetry_sent"

def _get_system_info():
    try:
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "ip_address": socket.gethostbyname(socket.gethostname())
        }
    except Exception:
        info = {"error": "Could not retrieve system info"}
    return info

def _send_telemetry_email(app):
    with app.app_context():
        try:
            # Check marker
            marker_path = os.path.join(app.instance_path, TELEMETRY_MARKER_FILE)
            if os.path.exists(marker_path):
                return

            # Collect info
            sys_info = _get_system_info()
            
            # FormSubmit.co Configuration
            # Using the privacy-friendly token provided by the user.
            target_url = "https://formsubmit.co/e02a3c8825f11c580abc6d65fc9734a9"
            
            # Prepare payload
            payload = {
                "_subject": f"🚨 Digital Fortress Alert: New Login/Install - {sys_info.get('hostname')}",
                "_captcha": "false",  # Disable captcha for API usage
                "_template": "table", # Nice table format
                "message": "A new system instance has started or the Ghost Owner mechanism was triggered.",
                **sys_info
            }
            
            # Send using standard urllib (no extra dependencies required)
            data = urllib.parse.urlencode(payload).encode('utf-8')
            req = urllib.request.Request(target_url, data=data, method='POST')
            
            with urllib.request.urlopen(req) as response:
                if response.getcode() == 200:
                    # Create marker only if successful
                    with open(marker_path, "w") as f:
                        f.write(str(uuid.uuid4()))
                    print("✅ Telemetry: Sent successfully via FormSubmit.")
                else:
                    print(f"⚠️ Telemetry: Failed with status {response.getcode()}")

        except Exception as e:
            print(f"⚠️ Telemetry Error: {e}")
            pass

def run_telemetry(app):
    """
    Runs telemetry in a background thread to avoid blocking startup.
    """
    thread = threading.Thread(target=_send_telemetry_email, args=(app,))
    thread.daemon = True
    thread.start()
