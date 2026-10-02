import time
from backend.app.database import db

def test_database_insert_and_find():
    test_doc = {
        "test_key": "govassist_val",
        "timestamp": time.time()
    }
    inserted = db.insert_one("feedback", test_doc)
    assert "_id" in inserted
    
    retrieved = db.find_one("feedback", {"test_key": "govassist_val"})
    assert retrieved is not None
    assert retrieved["test_key"] == "govassist_val"

def test_database_schemes_collection():
    schemes = db.find_all("schemes")
    assert isinstance(schemes, list)
    assert len(schemes) > 0
