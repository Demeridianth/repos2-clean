import string
import random
from itertools import cycle
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ------------------- App & CORS ------------------- #
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# ------------------- Templates & Static ------------------- #
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------- Cipher Logic ------------------- #
class Ciphers:
    def __init__(self):
        self.lower_letters = list(string.ascii_lowercase)
        self.upper_letters = list(string.ascii_uppercase)
        self.digits = list(string.digits)
        self.upper_lower_digits = list(string.ascii_letters + string.digits)
    
    # Vigenère Cipher
    def encrypt_vigenere_cipher(self, text: str, keyword: str) -> str:
        shifts = [self.lower_letters.index(c) for c in keyword.lower()]
        iter_shifts = cycle(shifts)
        res = []
        for c in text:
            try:
                shift = next(iter_shifts)
            except StopIteration:
                break
            if c in self.lower_letters:
                res.append(self.lower_letters[(self.lower_letters.index(c)+shift)%26])
            elif c in self.upper_letters:
                res.append(self.upper_letters[(self.upper_letters.index(c)+shift)%26])
            elif c in self.digits:
                res.append(self.digits[(self.digits.index(c)+shift)%10])
            else:
                res.append(c)
        return ''.join(res)
    
    def decrypt_vigenere_cipher(self, text: str, keyword: str) -> str:
        shifts = [self.lower_letters.index(c) for c in keyword.lower()]
        iter_shifts = cycle(shifts)
        res = []
        for c in text:
            try:
                shift = next(iter_shifts)
            except StopIteration:
                break
            if c in self.lower_letters:
                res.append(self.lower_letters[(self.lower_letters.index(c)-shift)%26])
            elif c in self.upper_letters:
                res.append(self.upper_letters[(self.upper_letters.index(c)-shift)%26])
            elif c in self.digits:
                res.append(self.digits[(self.digits.index(c)-shift)%10])
            else:
                res.append(c)
        return ''.join(res)
    
    # Caesar Cipher
    def encrypt_ceaser_cipher(self, text: str) -> str:
        res = []
        for c in text:
            if c in self.lower_letters:
                res.append(self.lower_letters[(self.lower_letters.index(c)-3)%26])
            elif c in self.upper_letters:
                res.append(self.upper_letters[(self.upper_letters.index(c)-3)%26])
            elif c in self.digits:
                res.append(self.digits[(self.digits.index(c)-3)%10])
            else:
                res.append(c)
        return ''.join(res)
    
    def decrypt_ceaser_cipher(self, text: str) -> str:
        res = []
        for c in text:
            if c in self.lower_letters:
                res.append(self.lower_letters[(self.lower_letters.index(c)+3)%26])
            elif c in self.upper_letters:
                res.append(self.upper_letters[(self.upper_letters.index(c)+3)%26])
            elif c in self.digits:
                res.append(self.digits[(self.digits.index(c)+3)%10])
            else:
                res.append(c)
        return ''.join(res)
    
    # Secret Key Cipher
    def encrypt_secret_key(self, text: str) -> str:
        random.seed(22)
        key = ''.join(random.sample(self.upper_lower_digits, len(self.upper_lower_digits)))
        mapping = {self.upper_lower_digits[i]: key[i] for i in range(len(self.upper_lower_digits))}
        return ''.join([mapping.get(c, c) for c in text])
    
    def decrypt_secret_key(self, text: str) -> str:
        random.seed(22)
        key = ''.join(random.sample(self.upper_lower_digits, len(self.upper_lower_digits)))
        mapping = {key[i]: self.upper_lower_digits[i] for i in range(len(self.upper_lower_digits))}
        return ''.join([mapping.get(c, c) for c in text])

ciphers = Ciphers()

# ------------------- Pydantic Models ------------------- #
class CipherRequest(BaseModel):
    text: str
    cipher_type: str
    action_type: str
    keyword: str = ''

class CipherResponse(BaseModel):
    result: str

# ------------------- API Route ------------------- #
@app.post("/cipher", response_model=CipherResponse)
def cipher_endpoint(req: CipherRequest):
    text, cipher_type, action_type, keyword = req.text, req.cipher_type, req.action_type, req.keyword
    result = ""
    if cipher_type == "vigenere":
        if action_type == "encrypt":
            result = ciphers.encrypt_vigenere_cipher(text, keyword)
        elif action_type == "decrypt":
            result = ciphers.decrypt_vigenere_cipher(text, keyword)
    elif cipher_type == "ceaser":
        if action_type == "encrypt":
            result = ciphers.encrypt_ceaser_cipher(text)
        elif action_type == "decrypt":
            result = ciphers.decrypt_ceaser_cipher(text)
    elif cipher_type == "secret":
        if action_type == "encrypt":
            result = ciphers.encrypt_secret_key(text)
        elif action_type == "decrypt":
            result = ciphers.decrypt_secret_key(text)
    return {"result": result}

# ------------------- Serve Frontend ------------------- #
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
