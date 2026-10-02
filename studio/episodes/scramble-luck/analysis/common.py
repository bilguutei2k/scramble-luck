"""Paths, provenance and small output helpers; never imports confirmation times."""
from pathlib import Path
import hashlib, json, datetime
import numpy as np

OUT = Path(__file__).resolve().parent
EP = OUT.parent
ROOT = EP.parents[2]
DERIVED = EP / 'data/derived'
PILOT = ROOT / 'ideation/rounds/r5/pilot-S1'
SEED = 20261001
NOTICE = ('This information is based on competition results owned and maintained by '
          'the World Cube Assocation, published at https://worldcubeassociation.org/results '
          'as of September 30, 2026.')
FROZEN = json.loads((PILOT / 'frozen-model.json').read_text())
BETA = np.array(FROZEN['hyperparameters']['position'])

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(2**20), b''): h.update(b)
    return h.hexdigest()

def dump(name, obj):
    def convert(x):
        if isinstance(x, np.ndarray): return x.tolist()
        if isinstance(x, np.generic): return x.item()
        if isinstance(x, Path): return str(x)
        raise TypeError(type(x).__name__)
    (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True, default=convert,
                                      allow_nan=False) + '\n')

def progress(message):
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    with (OUT / 'PROGRESS.md').open('a') as f: f.write(f'\n- {stamp}: {message}\n')
    print(message[:600], flush=True)

def code_hashes():
    return {p.name: sha(p) for p in sorted(OUT.glob('*.py'))}
