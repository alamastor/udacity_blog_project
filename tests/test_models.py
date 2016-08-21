from datetime import datetime

from blog.models import Post


def test_Post_has_correct_fields():
    assert 'title' in Post._properties
    assert 'content' in Post._properties
    assert 'datetime' in Post._properties
    assert len(Post._properties) == 3
