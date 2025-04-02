from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate ECDSA key pair
private_key = ec.generate_private_key(ec.SECP256R1())

# Convert private key to base64 URL
private_bytes = private_key.private_numbers().private_value.to_bytes(32, "big")
private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode("utf-8").rstrip("=")

# Extract public key in the right format
public_numbers = private_key.public_key().public_numbers()
public_key_raw = b"\x04" + public_numbers.x.to_bytes(32, "big") + public_numbers.y.to_bytes(32, "big")
public_key_b64 = base64.urlsafe_b64encode(public_key_raw).decode("utf-8").rstrip("=")

print("Public Key:", public_key_b64)
print("Private Key:", private_key_b64)
