"""
Smoke test: verify new YouTube content surfaces in semantic search
Run after merge_youtube_knowledge.py + build_embeddings.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

KNOWLEDGE_JSON = "beervanon_cleaned.json"
EMBEDDINGS_FILE = "embeddings.npz"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5

# Queries that target NEW YT content (Beer Vanon YouTube playlist 27)
QUERIES = [
    "การเตรียมตัวเป็น Full Time Trader",
    "Warrant ความโหดและเกมส์ที่เปลี่ยนไป",
    "แนวทางการฝึกฝนตัวเอง Beer Survivor",
    "เดิมพันแบบสมควรเสีย",
    "การหาการบ้านเทรด",
    "บทเรียน 2023 เทรดเดอร์",
    "วงจร 6 เฟส เทรดหุ้น",  # control: from FB content
]


def main():
    print("Loading knowledge base + embeddings...")
    posts = json.loads(Path(KNOWLEDGE_JSON).read_text(encoding="utf-8"))
    embeddings = np.load(EMBEDDINGS_FILE)["embeddings"]
    print(f"  posts: {len(posts)}, embeddings: {embeddings.shape}")

    yt_count = sum(1 for p in posts if "youtube.com" in p.get("url", ""))
    fb_count = len(posts) - yt_count
    print(f"  YouTube: {yt_count}, Facebook: {fb_count}")

    print(f"\nLoading embedding model {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)

    for q in QUERIES:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print('='*70)
        q_emb = model.encode([q], normalize_embeddings=True)[0]
        sims = embeddings @ q_emb
        top_idx = np.argsort(sims)[-TOP_K:][::-1]
        for rank, i in enumerate(top_idx, 1):
            p = posts[i]
            src = "YT" if "youtube.com" in p.get("url", "") else "FB"
            title = p.get("content", "")[:60].replace("\n", " ")
            print(f"  {rank}. [{src}] sim={sims[i]:.3f} {title}")


if __name__ == "__main__":
    main()
