
from app.memory_v2.models import Observation
from app.memory_v2.storage.sqlite_store import SQLiteMemoryStore

def test_sqlite_persistence(tmp_path):
    db=SQLiteMemoryStore(tmp_path/"memory.db")
    x=Observation("1","ITEM_RECEIVED",{"item_id":5},"tcp")
    db.save_observation(x)
    assert db.count("observations")==1
    db.close()
    db2=SQLiteMemoryStore(tmp_path/"memory.db")
    assert db2.count("observations")==1
    db2.close()
