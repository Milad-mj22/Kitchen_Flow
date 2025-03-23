from pywebpush import generate_vapid_keys

public_key, private_key = generate_vapid_keys()

print("Public Key:", public_key)
print("Private Key:", private_key)
