import hashlib, os

salt = os.urandom(16).hex()
password = "UsFEvZXZomWorB3eJVbA"
hash_ = hashlib.sha256((password + salt).encode()).hexdigest()

print("salt:", salt)
print("hash:", hash_)
