#!/usr/bin/env python3
"""Reproducible nested-zlib representation experiment. Python standard library only."""
import argparse, hashlib, json, math, random, zlib
from collections import Counter
from pathlib import Path

def entropy1(data):
    n=len(data)
    if not n: return 0.0
    return -sum((c/n)*math.log2(c/n) for c in Counter(data).values())

def row(data, previous=None, round_no=0):
    counts=Counter(data); n=len(data)
    tv=None
    if previous is not None:
        prev=Counter(previous); pn=len(previous)
        tv=0.5*sum(abs(counts.get(i,0)/n-prev.get(i,0)/pn) for i in range(256))
    return {"round":round_no,"bytes":n,"entropy1_bits_per_byte":round(entropy1(data),6),
            "unique_byte_values":len(counts),
            "histogram_total_variation":None if tv is None else round(tv,6),
            "sha256":hashlib.sha256(data).hexdigest()}

def make_datasets():
    rng=random.Random(20261108)
    raw_random=bytes(rng.randrange(256) for _ in range(4096))
    return {
      "zeros":bytes(4096),
      "periodic_text":(b"TIMDR chronoprocess information dynamics; "*120)[:4096],
      "random_seed_20261108":raw_random,
      "already_zlib_compressed_random":zlib.compress(bytes(random.Random(20261109).randrange(256) for _ in range(4096)),9),
    }

def run(rounds=20):
    results={}
    for name, original in make_datasets().items():
        layers=[original]
        for _ in range(rounds):
            layers.append(zlib.compress(layers[-1],level=9))
        decoded=layers[-1]
        for _ in range(rounds):
            decoded=zlib.decompress(decoded)
        results[name]={"original_bytes":len(original),
          "rounds":[row(x,layers[i-1] if i else None,i) for i,x in enumerate(layers)],
          "roundtrip_ok":decoded==original,
          "original_sha256":hashlib.sha256(original).hexdigest(),
          "decoded_sha256":hashlib.sha256(decoded).hexdigest()}
    return {"experiment":"nested zlib compression","zlib_version":zlib.ZLIB_VERSION,
            "level":9,"rounds":rounds,"seed":20261108,"datasets":results}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--rounds",type=int,default=20)
    parser.add_argument("--output",default="compression_idr_results.json")
    args=parser.parse_args()
    result=run(args.rounds)
    Path(args.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
    for name,data in result["datasets"].items():
        print(f"{name}: {data['original_bytes']} -> {data['rounds'][-1]['bytes']} bytes; exact recovery={data['roundtrip_ok']}")
    print(f"Saved: {args.output}")
