import os
import sys
import time
import base64
import hashlib
import uuid
import socket
import webbrowser
import subprocess
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ===== Terminal Colors =====
class Colors:
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    WHITE = "\033[1;37m"
    CYAN = "\033[1;36m"
    GRAY = "\033[1;90m"
    RESET = "\033[0m"

# ===== AES Key (token_gen.py နဲ့တူရမယ်) =====
KEY_HEX = "000102030405060708090a0b0c0d0e0f"
key = bytes.fromhex(KEY_HEX)

def decrypt_with_iv(iv_hex: str, encrypted_b64: str) -> str:
    try:
        iv = bytes.fromhex(iv_hex)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted_padded = cipher.decrypt(encrypted_bytes)
        pad_len = decrypted_padded[-1]
        return decrypted_padded[:-pad_len].decode('utf-8')
    except Exception as e:
        print(f"{Colors.RED}❌ Decrypt error: {e}{Colors.RESET}")
        return None

def resolve_url_from_token(token: str) -> str:
    # ရှေ့ဆုံးက "token" ဆိုတဲ့စာလုံးကို ဖယ်ရှားမယ်
    if token.startswith("token"):
        token = token[5:]
    else:
        print(f"{Colors.RED}❌ Token က 'token' နဲ့ မစပါ။{Colors.RESET}")
        return None
    
    # ကျန်တဲ့အထဲက ရှေ့ဆုံး ၁၀ လုံးက random prefix (ဖယ်လိုက်မယ်)
    if len(token) <= 42:  # 10 prefix + 32 iv_hex
        print(f"{Colors.RED}❌ Token မမှန်ပါ။ (အနည်းဆုံး ၄၃ လုံးရှိရမယ်){Colors.RESET}")
        return None
    
    token = token[10:]  # prefix ၁၀ လုံးကို ဖယ်
    
    # နောက် ၃၂ လုံးက iv_hex ဖြစ်တယ်
    iv_hex = token[:32]
    encrypted_b64 = token[32:]
    
    return decrypt_with_iv(iv_hex, encrypted_b64)

def clear_terminal():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_progress(duration: float = 0.3, label: str = "Processing"):
    stages = ["■■▢▢▢▢▢▢▢▢", "■■■■■■▢▢▢▢", "■■■■■■■■■■"]
    for s in stages:
        sys.stdout.write(f"\r {Colors.CYAN}⚙ {Colors.WHITE}{label:<20} {s}{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(duration)
    sys.stdout.write(f"\r {Colors.GREEN}✔ {label:<20} [DONE]{Colors.RESET}\n")
    sys.stdout.flush()

def get_auto_mac():
    try:
        mac = hex(uuid.getnode())[2:].zfill(12)
        return ":".join(mac[i:i+2] for i in range(0, 12, 2))
    except:
        return "88:2f:92:d4:c9:e0"

def get_gateway():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        parts = ip.split('.')
        if parts[0] in ["192", "10", "172"]:
            parts[-1] = "1"
            return ".".join(parts)
    except:
        pass
    return "192.168.110.1"

def modify_url_parameter(url: str, param: str, value: str) -> str:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs[param] = [value]
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params,
                       urlencode(qs, doseq=True), parsed.fragment))

def main():
    clear_terminal()

    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════╗")
    print(f"{Colors.CYAN}║          ✦  ENTER YOUR TOKEN  ✦                                   ║")
    print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    token = input(f"{Colors.YELLOW}🔑 Token ကို ကူးထည့်ပါ: {Colors.RESET}").strip()

    if not token:
        print(f"{Colors.RED}❌ Token မပါပါ။{Colors.RESET}")
        return

    print(f"\n{Colors.CYAN}⏳ Token ကို ဖြေနေပါသည်...{Colors.RESET}")
    url = resolve_url_from_token(token)

    if not url:
        print(f"{Colors.RED}❌ Token မှားနေပါသည်။{Colors.RESET}")
        return

    print(f"{Colors.GREEN}✅ SS URL ကို အောင်မြင်စွာ ပြန်ထုတ်လိုက်ပါပြီ။{Colors.RESET}")

    # ===== MAC Address ကို ကိုယ်တိုင်ထည့်ခိုင်းမယ် =====
    auto_mac = get_auto_mac()
    print(f"\n{Colors.YELLOW}📌 Auto-detect MAC Address: {auto_mac}{Colors.RESET}")
    manual_mac = input(f"{Colors.CYAN}✏️  MAC Address ထည့်ပါ (Enter နှိပ်ရင် auto-detect လုပ်မည်): {Colors.RESET}").strip()

    if manual_mac:
        mac = manual_mac
        print(f"{Colors.GREEN}✅ သင်ထည့်လိုက်တဲ့ MAC ကို သုံးပါမည်။{Colors.RESET}")
    else:
        mac = auto_mac
        print(f"{Colors.GRAY}⏩ Auto-detect MAC ကို သုံးပါမည်။{Colors.RESET}")

    gw = get_gateway()

    print(f"\n{Colors.CYAN}┌───────────────────────── System Info ─────────────────────────┐")
    print(f"{Colors.CYAN}│ {Colors.WHITE}MAC: {Colors.YELLOW}{mac:<18} {Colors.WHITE}Gateway: {Colors.YELLOW}{gw:<17}{Colors.CYAN}│")
    print(f"{Colors.CYAN}└──────────────────────────────────────────────────────────────────────┘{Colors.RESET}\n")

    print_progress(0.3, "Resolving URL")
    print_progress(0.3, "Binding Device")

    processed_url = modify_url_parameter(url, 'mac', mac)

    print(f"\n{Colors.GREEN}🌐 Opening portal...{Colors.RESET}")
    time.sleep(0.5)

    try:
        subprocess.run(["termux-open-url", processed_url], check=True, timeout=5)
        print(f"{Colors.GREEN}✅ Portal opened (Termux).{Colors.RESET}")
    except:
        try:
            webbrowser.open(processed_url)
            print(f"{Colors.GREEN}✅ Portal opened (Browser).{Colors.RESET}")
        except:
            print(f"\n{Colors.YELLOW}အောက်ပါလင့်ခ်ကို ကိုယ်တိုင်ဖွင့်ပါ:\n{processed_url}{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}⚠ Stopped by user.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()