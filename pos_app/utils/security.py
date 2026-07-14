import hashlib
import os

def hash_password(password: str) -> str:
    """Generate a secure sha256 hash of the password with salt."""
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{hashed.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify standard PBKDF2 hash of a password."""
    try:
        salt_hex, hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return computed_hash == expected_hash
    except (ValueError, AttributeError):
        return False
