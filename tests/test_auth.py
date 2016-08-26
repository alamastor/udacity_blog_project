from blog import auth


def test_make_pw_hash_returns_256_bit_str():
    digest = auth.make_pw_hash('user', 'pass', '1231')
    assert type(digest) is str
    assert len(digest) == 64


def test_make_secure_val_returns_256_bit_str():
    digest = auth.make_secure_val(123)
    assert type(digest) is str
    assert len(digest) == 64


def test_check_secure_val_returns_true_for_valid_input():
    digest = auth.make_secure_val(123)
    assert auth.check_secure_val(123, digest) is True


def test_check_secure_val_returns_false_for_invalid_input():
    digest = auth.make_secure_val(123)
    assert auth.check_secure_val(125, digest) is False
