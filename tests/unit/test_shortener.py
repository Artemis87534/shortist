from src.links.crud import generate_short_id

def test_generate_short_id_length():
    """Test that generated ID has correct length"""
    short_id = generate_short_id()
    assert len(short_id) == 6

def test_generate_short_id_uniqueness():
    """Test that generated IDs are unique"""
    ids = {generate_short_id() for _ in range(1000)}
    assert len(ids) == 1000