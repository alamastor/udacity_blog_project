from hashlib import sha256
import hmac
from ConfigParser import SafeConfigParser
import os
import binascii

from models.models import User

config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'auth.cfg'))
HMAC_SESSION_KEY = config.get('Keys', 'session')


def make_pw_hash(username, password, salt):
    return sha256(username + password + salt).hexdigest()


def make_secure_val(val):
    return hmac.new(HMAC_SESSION_KEY, str(val), sha256).hexdigest()


def check_secure_val(val, hexdigest):
    return constant_time_compare(
        make_secure_val(val),
        str(hexdigest)
    )


def create_user(username, password, email=None):
    salt = make_salt()
    user = User(
        username=username,
        pw_hash=make_pw_hash(username, password, salt),
        salt=salt,
        email=email
    )
    user.put()
    return user.key.id()


def make_salt():
    return binascii.hexlify(os.urandom(4))


def constant_time_compare(a, b):
    """Return ``a == b`` using an approach resistant to timing analysis.

    a and b must both be of the same type: either both text strings,
    or both byte strings.

    Note: If a and b are of different lengths, or if an error occurs,
    a timing attack could theoretically reveal information about the
    types and lengths of a and b, but not their values.

    Function from taken from
    https://www.reddit.com/r/Python/comments/49hwq0/constant_time_comparison_in_python/
    as a replacement for hmac.compare_digest, which is not available in
    the Python version on Google App Engine 2.7.5.
    """
    for T in (bytes, unicode):
        if isinstance(a, T) and isinstance(b, T):
            break
    else:
        raise TypeError("arguments must be both strings or both bytes")
    if len(a) != len(b):
        return False
    result = True
    for x, y in zip(a, b):
        # VERY IMPORTANT: do **not** short-cut early. It is vital
        # that all comparisons take the same amount of time.
        result &= (x == y)
    return result
