from hashlib import sha256
import hmac
from ConfigParser import SafeConfigParser
import os

config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'auth.cfg'))
HMAC_SESSION_KEY = config.get('Keys', 'session')


def make_pw_hash(username, password, salt):
    return sha256(username + password + salt).hexdigest()


def make_secure_val(val):
    return hmac.new(HMAC_SESSION_KEY, str(val), sha256).hexdigest()


def check_secure_val(val, hexdigest):
    return hmac.compare_digest(
        make_secure_val(val),
        str(hexdigest)
    )
