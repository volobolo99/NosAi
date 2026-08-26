"""Build review-only candidate patches from public NosTale references.

The boxes are weak visual hints. Generated patches are marked weak_reference and
must not be promoted to production entity templates without local ground truth.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/"data/vision/reference_sources.json"
HINTS=ROOT/"data/vision/reference_entity_hints.json"

def fetch(url):
    req=Request(url,headers={"User-Agent":"NosAi-vision-reference/1.0"})
    with urlopen(req,timeout=20) as r: return r.read()

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,default=ROOT/".nosai/vision/reference_candidates");a=p.parse_args()
    try:
        import cv2, numpy as np
    except ImportError as e: raise SystemExit("Install vision dependencies: pip install -e '.[vision]'") from e
    sources={x["id"]:x for x in json.loads(SOURCES.read_text())["sources"]}
    hints=json.loads(HINTS.read_text())["sources"]
    a.output.mkdir(parents=True,exist_ok=True); manifest=[]
    for rid, boxes in hints.items():
        if rid not in sources: continue
        try: data=fetch(sources[rid]["url"]); image=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
        except Exception as e: manifest.append({"source":rid,"status":"unavailable","error":str(e)});continue
        if image is None: manifest.append({"source":rid,"status":"invalid"});continue
        h,w=image.shape[:2]
        for i,b in enumerate(boxes):
            x,y,bw,bh=b["box"]; x0=max(0,int(x*w));y0=max(0,int(y*h));x1=min(w,int((x+bw)*w));y1=min(h,int((y+bh)*h))
            if x1<=x0 or y1<=y0: continue
            out=a.output/f"{rid}_{i}_{b['kind']}.png";cv2.imwrite(str(out),image[y0:y1,x0:x1])
            manifest.append({"kind":b["kind"],"path":str(out.relative_to(ROOT)),"source":rid,"source_confidence":b["confidence"],"status":"candidate_only"})
    (a.output/"manifest.json").write_text(json.dumps({"policy":"candidate_only","ground_truth_required":True,"items":manifest},indent=2))
    print(json.dumps({"candidates":len([x for x in manifest if x.get('status')=='candidate_only']),"ground_truth_required":True}))
if __name__=="__main__": raise SystemExit(main())
