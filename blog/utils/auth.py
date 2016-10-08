from hashlib import sha256
import hmac
from ConfigParser import SafeConfigParser
import os
import binascii

from models.user import User

# Read key from auth.cfg for use with HMAC.
config = SafeConfigParser()
if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    auth_conf = 'example_auth.cfg'
else:
    auth_conf = 'auth.cfg'
config.read(os.path.join(os.path.dirname(__file__), '..', auth_conf))
HMAC_SESSION_KEY = config.get('Keys', 'session')


def make_pw_hash(username, password, salt):
    ''' Generate password hash from usename, password & salt.
    '''
    return sha256(username + password + salt).hexdigest()


def make_secure_val(val):
    ''' Generate a hashed of string, using HMAC.
    '''
    return hmac.new(HMAC_SESSION_KEY, str(val), sha256).hexdigest()


def check_secure_val(val, hexdigest):
    ''' Verify a value matches a hash.
    '''
    return constant_time_compare(make_secure_val(val), str(hexdigest))


def create_user(username, password, email=None):
    ''' Add a new user to database, with a hashed password, and salt.
    '''
    salt = make_salt()

    if User.get_by_username(username):
        raise UserAlreadyExists("user '%s' already exists" % username)

    user = User(
        username=username,
        pw_hash=make_pw_hash(username, password, salt),
        salt=salt,
        email=email
    )
    user.put()
    return user.key.id()


def make_salt():
    ''' Generate a salt string, for use in generating password hash.
    '''
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
    if isinstance(a, str):
        # Convert str to uncode if required.
        a = unicode(a)
    if isinstance(b, str):
        b = unicode(b)
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


class UserAlreadyExists(Exception):
    pass
