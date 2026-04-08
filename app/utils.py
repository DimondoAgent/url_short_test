import secrets
#used secrets module instead of random to generate cryptographically secure short codes,
#which is important for preventing collisions and ensuring the uniqueness of short URLs
import string

ALPHABET = string.ascii_letters + string.digits

def generate_short_string(length: int = 7) -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))