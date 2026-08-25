from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from typing import Callable,Iterable,Any

class ParallelSimulation:
    def run(self,fn,inputs,workers=4):
        workers=max(1,int(workers));
        with ThreadPoolExecutor(max_workers=workers) as ex:return list(ex.map(fn,inputs))
    def benchmark(self,fn,inputs,workers=4):
        t=perf_counter();out=self.run(fn,inputs,workers);elapsed=perf_counter()-t;return {'results':out,'seconds':elapsed,'count':len(out),'throughput':len(out)/(elapsed or 1e-9)}

class ComputeProfiler:
    def measure(self,fn,*args,**kwargs):t=perf_counter();r=fn(*args,**kwargs);return r,perf_counter()-t
    def profile(self,functions):return {name:self.measure(fn)[1] for name,fn in functions.items()}

class MCTSOptimizer:
    def simulations(self,uncertainty,base=64,maximum=1024):return min(maximum,max(base,int(base*(1+uncertainty))))
    def schedule(self,uncertainty,risk,base=64,maximum=1024):return min(maximum,max(base,int(base*(1+max(uncertainty,risk)*2))))

class MemoryIndex:
    def __init__(self):self._index={}
    def add(self,key,value):self._index.setdefault(key,[]).append(value)
    def get(self,key):return list(self._index.get(key,()))
    def remove(self,key,value):
        if key in self._index and value in self._index[key]:self._index[key].remove(value)
        if key in self._index and not self._index[key]:del self._index[key]
    def size(self):return sum(len(v) for v in self._index.values())
    def rebuild(self,rows):self._index={};[self.add(k,v) for k,v in rows];return self.size()
