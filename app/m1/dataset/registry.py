import hashlib, json
class DatasetRegistry:
    def __init__(self): self._items={}
    def register(self, manifest): self._items[manifest.dataset_id]=manifest; return manifest.dataset_id
    def get(self,dataset_id): return self._items[dataset_id]
    def verify(self,dataset_id): return bool(self._items.get(dataset_id))
    def compare(self,a,b):
        x,y=self.get(a),self.get(b); return {k:(getattr(x,k),getattr(y,k)) for k in x.__dataclass_fields__ if getattr(x,k)!=getattr(y,k)}

def checksum_bytes(data: bytes): return hashlib.sha256(data).hexdigest()
def canonical_manifest(manifest): return json.dumps(manifest.__dict__,sort_keys=True,separators=(',',':'))
