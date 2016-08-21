from hashlib import sha256


def make_pw_hash(username, password, salt):
    return sha256(username + password + salt).hexdigest()
