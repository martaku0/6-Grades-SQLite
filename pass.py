import hashlib

passwd = 'zaq1@WSX'.encode()
print(hashlib.sha256(passwd).hexdigest())