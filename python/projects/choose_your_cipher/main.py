import string
import random
from itertools import cycle
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ======================
# CORS for frontend dev
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ======================
# Cipher logic
# ======================
class Ciphers:
    def __init__(self):
        self.lower_letters = list(string.ascii_lowercase)
        self.upper_letters = list(string.ascii_uppercase)
        self.digits = list(string.digits)
        self.all_chars = self.lower_letters + self.upper_letters + self.digits

    # --- Vigenère Cipher ---
    def encrypt_vigenere_cipher(self, text: str, keyword: str) -> str:
        keyword_shift = [self.lower_letters.index(c.lower()) for c in keyword if c.lower() in self.lower_letters]
        encoded = []
        iter_shift = cycle(keyword_shift)
        for char in text:
            shift = next(iter_shift, 0)
            if char in self.lower_letters:
                idx = self.lower_letters.index(char)
                encoded.append(self.lower_letters[(idx + shift) % 26])
            elif char in self.upper_letters:
                idx = self.upper_letters.index(char)
                encoded.append(self.upper_letters[(idx + shift) % 26])
            elif char in self.digits:
                idx = self.digits.index(char)
                encoded.append(self.digits[(idx + shift) % 10])
            else:
                encoded.append(char)
        return ''.join(encoded)

    def decrypt_vigenere_cipher(self, text: str, keyword: str) -> str:
        keyword_shift = [self.lower_letters.index(c.lower()) for c in keyword if c.lower() in self.lower_letters]
        decoded = []
        iter_shift = cycle(keyword_shift)
        for char in text:
            shift = next(iter_shift, 0)
            if char in self.lower_letters:
                idx = self.lower_letters.index(char)
                decoded.append(self.lower_letters[(idx - shift) % 26])
            elif char in self.upper_letters:
                idx = self.upper_letters.index(char)
                decoded.append(self.upper_letters[(idx - shift) % 26])
            elif char in self.digits:
                idx = self.digits.index(char)
                decoded.append(self.digits[(idx - shift) % 10])
            else:
                decoded.append(char)
        return ''.join(decoded)

    # --- Caesar Cipher ---
    def encrypt_caesar_cipher(self, text: str) -> str:
        result = []
        for char in text:
            if char in self.lower_letters:
                idx = self.lower_letters.index(char)
                result.append(self.lower_letters[(idx - 3) % 26])
            elif char in self.upper_letters:
                idx = self.upper_letters.index(char)
                result.append(self.upper_letters[(idx - 3) % 26])
            elif char in self.digits:
                idx = self.digits.index(char)
                result.append(self.digits[(idx - 3) % 10])
            else:
                result.append(char)
        return ''.join(result)

    def decrypt_caesar_cipher(self, text: str) -> str:
        result = []
        for char in text:
            if char in self.lower_letters:
                idx = self.lower_letters.index(char)
                result.append(self.lower_letters[(idx + 3) % 26])
            elif char in self.upper_letters:
                idx = self.upper_letters.index(char)
                result.append(self.upper_letters[(idx + 3) % 26])
            elif char in self.digits:
                idx = self.digits.index(char)
                result.append(self.digits[(idx + 3) % 10])
            else:
                result.append(char)
        return ''.join(result)

    # --- Secret Key Cipher ---
    def encrypt_secret_key(self, text: str) -> str:
        random.seed(22)
        key = ''.join(random.sample(self.all_chars, len(self.all_chars)))
        mapping = {self.all_chars[i]: key[i] for i in range(len(self.all_chars))}
        return ''.join([mapping.get(c, c) for c in text])

    def decrypt_secret_key(self, text: str) -> str:
        random.seed(22)
        key = ''.join(random.sample(self.all_chars, len(self.all_chars)))
        mapping = {key[i]: self.all_chars[i] for i in range(len(self.all_chars))}
        return ''.join([mapping.get(c, c) for c in text])


ciphers = Ciphers()

# ======================
# Pydantic Models
# ======================
class CipherRequest(BaseModel):
    text: str
    action_type: str  # "encrypt" or "decrypt"
    cipher_type: str  # "vigenere", "caesar", "secret"
    keyword: str = ""  # only used for Vigenère

class CipherResponse(BaseModel):
    result: str

# ======================
# API Endpoint
# ======================
@app.post("/cipher", response_model=CipherResponse)
def cipher_endpoint(req: CipherRequest):
    text = req.text
    cipher_type = req.cipher_type.lower()
    action_type = req.action_type.lower()
    keyword = req.keyword
    result = ""

    if cipher_type == "vigenere":
        if action_type == "encrypt":
            result = ciphers.encrypt_vigenere_cipher(text, keyword)
        else:
            result = ciphers.decrypt_vigenere_cipher(text, keyword)
    elif cipher_type == "caesar":
        if action_type == "encrypt":
            result = ciphers.encrypt_caesar_cipher(text)
        else:
            result = ciphers.decrypt_caesar_cipher(text)
    elif cipher_type == "secret":
        if action_type == "encrypt":
            result = ciphers.encrypt_secret_key(text)
        else:
            result = ciphers.decrypt_secret_key(text)

    return {"result": result}
