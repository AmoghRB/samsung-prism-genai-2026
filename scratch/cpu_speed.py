import sys, time, os, json, numpy as np, torch
sys.path.insert(0,'scratch'); from bench import load
from sentence_transformers import SentenceTransformer
name=sys.argv[1]; variant=sys.argv[2]; th=int(sys.argv[3]) if len(sys.argv)>3 else 12
torch.set_num_threads(th)
D=load(); rng=np.random.RandomState(0)
docs=[list(D["corpus"].values())[i] for i in rng.choice(8765,192,replace=False)]
qs=[list(D["queries"].values())[i] for i in rng.choice(3765,64,replace=False)]
docs.sort(key=len, reverse=True); qs.sort(key=len, reverse=True)
kw={}
if variant=="bf16": kw=dict(model_kwargs={"torch_dtype":torch.bfloat16})
m=SentenceTransformer(name,device="cpu",trust_remote_code=True,**kw); m.max_seq_length=512
if variant=="qint8":
    m[0].auto_model=torch.ao.quantization.quantize_dynamic(m[0].auto_model,{torch.nn.Linear},dtype=torch.qint8)
ref=None
m.encode(docs[-8:])
t=time.time(); ed=m.encode(docs,batch_size=16); td=time.time()-t
t=time.time(); eq=m.encode(qs,batch_size=16); tq=time.time()-t
np.save(f"scratch/cache/cpu_{variant}_{name.split('/')[-1]}.npy", np.concatenate([ed,eq]))
print(json.dumps(dict(model=name,variant=variant,threads=th,docs_per_s=round(192/td,2),q_per_s=round(64/tq,2))))
