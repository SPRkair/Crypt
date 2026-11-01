import sys, os, secrets, hashlib, getpass
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import InvalidTag

def key_from(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt,
                          n=2**15, r=8, p=1, maxmem=64*1024*1024, dklen=32)

def free_name(path: str) -> str:
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{base}_{i}{ext}"):
        i += 1
    return f"{base}_{i}{ext}"

def encrypt(path: str, password: str):
    with open(path, "rb") as f:
        data = f.read()
    name = os.path.basename(path).encode("utf-8")
    if len(name) > 255:
        sys.exit("Слишком длинное имя файла.")
    plain = bytes([len(name)]) + name + data

    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    ct = ChaCha20Poly1305(key_from(password, salt)).encrypt(nonce, plain, None)

    out = os.path.join(os.path.dirname(os.path.abspath(path)),
                       secrets.token_hex(8) + ".crypted")
    with open(out, "wb") as f:
        f.write(salt + nonce + ct)   # без заголовков и сигнатур
    print("Готово:", out)

def decrypt(path: str, password: str):
    with open(path, "rb") as f:
        blob = f.read()
    if len(blob) < 16 + 12 + 16 + 1:
        sys.exit("Файл повреждён.")
    salt, nonce, ct = blob[:16], blob[16:28], blob[28:]
    try:
        plain = ChaCha20Poly1305(key_from(password, salt)).decrypt(nonce, ct, None)
    except InvalidTag:
        sys.exit("Неверная строка или файл повреждён.")

    n = plain[0]
    name = plain[1:1+n].decode("utf-8")
    out = free_name(os.path.join(os.path.dirname(os.path.abspath(path)),
                                 os.path.basename(name)))
    with open(out, "wb") as f:
        f.write(plain[1+n:])
    print("Расшифровано:", out)

def main():
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        sys.exit("Укажите существующий файл.")
    path = sys.argv[1]
    if path.lower().endswith(".crypted"):
        decrypt(path, getpass.getpass("Введите строку: "))
    else:
        p = getpass.getpass("Введите строку: ")
        if p != getpass.getpass("Повторите строку: "):
            sys.exit("Строки не совпадают.")
        encrypt(path, p)

if __name__ == "__main__":
    main()
