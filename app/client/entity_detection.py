"""Observation-only visual entity detection primitives for NosTale.

Detectors are deliberately confidence-scored and template/config driven. They never
send input, modify the client, or turn a visual guess into an action.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True)
class Detection:
    kind: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    source: str = "vision"
    observation_only: bool = True

@dataclass(frozen=True)
class Roi:
    name: str
    x: float
    y: float
    width: float
    height: float

def _crop(image, roi: Roi):
    h,w=image.shape[:2]
    x=max(0,min(w,int(w*roi.x)));y=max(0,min(h,int(h*roi.y)))
    rw=max(1,min(w-x,int(w*roi.width)));rh=max(1,min(h-y,int(h*roi.height)))
    return image[y:y+rh,x:x+rw],x,y

class VisualEntityDetector:
    """Detect player/NPC/mob candidates with optional OpenCV templates."""
    def __init__(self, templates: dict[str,str|Path]|None=None, threshold: float=.78):
        self.templates={k:Path(v) for k,v in (templates or {}).items()};self.threshold=threshold

    def detect_templates(self, image) -> tuple[Detection,...]:
        try:
            import cv2
        except ImportError as exc: raise RuntimeError("vision requires the optional 'vision' dependencies") from exc
        out=[]
        for kind,path in self.templates.items():
            if not path.exists(): continue
            template=cv2.imread(str(path),cv2.IMREAD_COLOR)
            if template is None: continue
            result=cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
            _,score,_,loc=cv2.minMaxLoc(result)
            if score>=self.threshold:
                h,w=template.shape[:2];out.append(Detection(kind,loc[0],loc[1],w,h,float(score)))
        return tuple(out)

    def detect(self, image, rois: Iterable[Roi]=()) -> tuple[Detection,...]:
        detections=list(self.detect_templates(image))
        # ROI metadata establishes deterministic search zones without guessing entity identity.
        for roi in rois:
            crop,x,y=_crop(image,roi)
            if crop.size: detections.append(Detection(f"roi:{roi.name}",x,y,crop.shape[1],crop.shape[0],1.0,source="roi"))
        return tuple(detections)

def default_rois() -> tuple[Roi,...]:
    return (Roi("world",.05,.08,.90,.82),Roi("minimap",.78,.02,.21,.25),Roi("hud",0,.78,1,.22))
