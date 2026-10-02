#!/usr/bin/env python3
"""Sequential follow-up jobs, launched after the paired sweep finishes."""
from pathlib import Path
import subprocess, sys, json, time
HERE=Path(__file__).resolve().parent

def main():
    jobs=[
        ('stability-large', ['run','--case','large_shared','--reps','20','--draws','2000','--output','stability.jsonl']),
        ('stability-boundary', ['run','--case','boundary','--reps','20','--draws','2000','--output','stability.jsonl']),
        ('replication-all', ['run','--start','1000','--output','replication.jsonl']),
        ('replication-boundary', ['run','--case','boundary','--start','1200','--reps','800','--output','replication.jsonl'])]
    timings=[]
    for name,args in jobs:
        start=time.perf_counter()
        print(json.dumps({'start':name}),flush=True)
        with (HERE/(name+'-progress.log')).open('w') as log:
            subprocess.run([sys.executable,str(HERE/'evaluate.py'),*args],stdout=log,stderr=subprocess.STDOUT,check=True)
        timings.append({'job':name,'wall_seconds':time.perf_counter()-start})
        (HERE/'followup-timing.json').write_text(json.dumps(timings,indent=2)+'\n')
        print(json.dumps(timings[-1]),flush=True)
    for args in ([],['--input','replication.jsonl','--prefix','replication-']):
        subprocess.run([sys.executable,str(HERE/'summarize.py'),*args],check=True)

if __name__=='__main__':main()
