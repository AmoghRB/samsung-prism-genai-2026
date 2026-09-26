import sys, time, os, json, numpy as np, torch
sys.path.insert(0,'scratch'); from bench import load
from sentence_transformers import SentenceTransformer
name=sys.argv[1]; th=int(sys.argv[2]); bs=int(sys.argv[3]) if len(sys.argv)>3 else 16
torch.set_num_threads(th)
D=load(); docs=list(D["corpus"].values())[:256]; qs=list(D["queries"].values())[:128]
m=SentenceTransformer(name,device="cpu",trust_remote_code=True); m.max_seq_length=512
m.encode(docs[:8])
t=time.time(); m.encode(docs,batch_size=bs); td=time.time()-t
t=time.time(); m.encode(qs,batch_size=bs); tq=time.time()-t
print(json.dumps(dict(model=name,threads=th,bs=bs,docs_per_s=round(256/td,1),q_per_s=round(128/tq,1),params_m=round(sum(p.numel() for p in m.parameters())/1e6))))
