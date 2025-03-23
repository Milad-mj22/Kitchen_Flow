from pywebpush import generate_vapid_keys

vapid_keys = generate_vapid_keys()
print("VAPID_PUBLIC_KEY:", vapid_keys["publicKey"])
print("VAPID_PRIVATE_KEY:", vapid_keys["privateKey"])
