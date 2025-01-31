import hashlib
import json
import pickle

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding

from src.common.helpers import Map


def generate_key_pair():
    # Generate a private key
    # private_key = rsa.generate_private_key(
    #     public_exponent=65537,
    #     key_size=2048,
    #     # key_size=1024,  # Reduced key size for faster generation
    # )
    private_key = ec.generate_private_key(
        ec.SECP256R1()
    )

    # Get the public key from the private key
    public_key = private_key.public_key()

    # Serialize the private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize the public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return Map({'pub_key': public_pem.decode('utf-8'), 'prv_key': private_pem.decode('utf-8')})


def sign_text(text, prv_key):
    # Sign the message using the node's private key
    private_key = serialization.load_pem_private_key(
        prv_key.encode(),
        password=None,
    )
    text = json.dumps(text).encode()
    signature = private_key.sign(
        text,
        # padding.PSS(
        #     mgf=padding.MGF1(hashes.SHA256()),
        #     salt_length=padding.PSS.MAX_LENGTH
        # ),
        # hashes.SHA256()
        ec.ECDSA(hashes.SHA256())
    )
    return signature


def calculate_hash(obj):
    try:
        data = json.dumps(obj, default=str).encode('utf-8')
    except (pickle.PicklingError, TypeError) as e:
        raise ValueError(f"Failed to serialize object: {e}")
    hash_data = hashlib.sha256()
    hash_data.update(data)

    return hash_data.hexdigest()
