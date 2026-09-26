"""Contrastive fine-tune of a small embedding model on the APPS *train* split only.

The test split (q5001+/d5001+) is never seen. 500 train pairs are held out for
validation so model selection does not touch the test set.

python scratch/finetune.py BASE_MODEL OUT_DIR [epochs] [qprefix]
"""
import os, sys, random
import pandas as pd
from huggingface_hub import hf_hub_download

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocess import preprocess_query

base, out = sys.argv[1], sys.argv[2]
epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 1
qprefix = sys.argv[4] if len(sys.argv) > 4 else ""
R = "CoIR-Retrieval/apps"
c = pd.read_parquet(hf_hub_download(R, "corpus/corpus-00000-of-00001.parquet", repo_type="dataset")).set_index("_id")
q = pd.read_parquet(hf_hub_download(R, "queries/queries-00000-of-00001.parquet", repo_type="dataset")).set_index("_id")
tr = pd.read_parquet(hf_hub_download(R, "data/train-00000-of-00001.parquet", repo_type="dataset"))
pairs = [(qprefix + preprocess_query(q.loc[a, "text"]), c.loc[b, "text"]) for a, b in zip(tr["query-id"], tr["corpus-id"])]
random.Random(0).shuffle(pairs)
val, train = pairs[:500], pairs[500:]

import torch
from datasets import Dataset
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.losses import CachedMultipleNegativesRankingLoss
from sentence_transformers.evaluation import InformationRetrievalEvaluator
from sentence_transformers.training_args import BatchSamplers

dev = "mps" if torch.backends.mps.is_available() else "cpu"
m = SentenceTransformer(base, device=dev, trust_remote_code=True)
m.max_seq_length = 512
ds = Dataset.from_dict({"anchor": [a for a, _ in train], "positive": [b for _, b in train]})
ev = InformationRetrievalEvaluator(
    queries={f"v{i}": a for i, (a, _) in enumerate(val)},
    corpus={f"d{i}": b for i, (_, b) in enumerate(val)},
    relevant_docs={f"v{i}": {f"d{i}"} for i in range(len(val))}, name="val", show_progress_bar=False)
print("before:", {k: v for k, v in ev(m).items() if "ndcg@10" in k})
loss = CachedMultipleNegativesRankingLoss(m, mini_batch_size=8)
args = SentenceTransformerTrainingArguments(
    output_dir=out + "_ckpt", num_train_epochs=epochs, per_device_train_batch_size=64,
    learning_rate=2e-5, warmup_ratio=0.1, batch_sampler=BatchSamplers.NO_DUPLICATES,
    logging_steps=10, save_strategy="no", eval_strategy="no", report_to=[], seed=0)
SentenceTransformerTrainer(model=m, args=args, train_dataset=ds, loss=loss).train()
print("after:", {k: v for k, v in ev(m).items() if "ndcg@10" in k})
m.save(out)
