import base64
import ecies


def generate_key_pair():
    """Generate a new cryptographic key pair"""
    key = ecies.utils.generate_key()
    secret = key.secret
    public = key.public_key.format(True)

    # Convert to bytes and then base64 for storage
    secret_b64 = base64.b64encode(secret).decode("utf-8")
    public_b64 = base64.b64encode(public).decode("utf-8")

    return secret_b64, public_b64


def decrypt_data(private_key, encrypted_data):
    """Decrypt data using the private key"""
    return ecies.decrypt(private_key, encrypted_data).decode("utf-8")


def encrypt_data(public_key, data):
    """Encrypt data using the public key"""
    return ecies.encrypt(public_key, data)