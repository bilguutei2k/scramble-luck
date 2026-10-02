#!/usr/bin/env python3
"""Exact four-edge cross distances, half-turn metric (18 unit-cost face moves).

An oriented edge is an ordered pair of perpendicular sticker normals. Four
labelled edges give 24^4 addresses; BFS visits exactly 12P4 * 2^4 = 190080
physically possible cross states. No solve-time input is accessible here.
"""
import re, time
import numpy as np
import pandas as pd
from numba import njit
from common import DERIVED, dump, progress, code_hashes, NOTICE

FACES = 'UDRLFB'
NORMALS = np.array([(0,1,0),(0,-1,0),(1,0,0),(-1,0,0),(0,0,1),(0,0,-1)])
PAIRS = [(a,b) for a in range(6) for b in range(6) if NORMALS[a] @ NORMALS[b] == 0]
PAIR_INDEX = {p:i for i,p in enumerate(PAIRS)}

def transition_table():
    table = np.empty((18,24),dtype=np.int32)
    for f, axis in enumerate(NORMALS):
        for i,(a,b) in enumerate(PAIRS):
            va,vb=NORMALS[a].copy(),NORMALS[b].copy()
            for turn in range(3):
                if (NORMALS[a]+NORMALS[b]) @ axis == 1:
                    va=-np.cross(axis,va)+axis*(axis@va)
                    vb=-np.cross(axis,vb)+axis*(axis@vb)
                aa=next(j for j,v in enumerate(NORMALS) if np.array_equal(v,va))
                bb=next(j for j,v in enumerate(NORMALS) if np.array_equal(v,vb))
                table[f*3+turn,i]=PAIR_INDEX[(aa,bb)]
    return table

@njit(cache=True)
def encode(q):
    return ((q[0]*24+q[1])*24+q[2])*24+q[3]

@njit(cache=True)
def bfs(table, goal):
    dist=np.full(24**4,255,dtype=np.uint8)
    queue=np.empty(190080,dtype=np.int32)
    start=encode(goal);dist[start]=0;queue[0]=start
    head=0;tail=1
    while head<tail:
        k=queue[head];head+=1
        a=k//13824;b=k//576%24;c=k//24%24;d=k%24
        for move in range(18):
            dest=((table[move,a]*24+table[move,b])*24+table[move,c])*24+table[move,d]
            if dist[dest]==255:
                dist[dest]=dist[k]+1;queue[tail]=dest;tail+=1
    return dist,tail

def moves(scramble):
    tokens=scramble.split()
    assert tokens and all(re.fullmatch("[UDRLFB](2|')?",t) for t in tokens), scramble
    return np.array([3*FACES.index(t[0])+(1 if t.endswith('2') else 2 if t.endswith("'") else 0)
                     for t in tokens],dtype=np.int32)

@njit(cache=True)
def face_lengths(seq, table, goals, distances):
    q=goals.copy()
    for m in seq:
        for f in range(6):
            for e in range(4):q[f,e]=table[m,q[f,e]]
    out=np.empty(6,dtype=np.int32)
    for f in range(6):out[f]=distances[f,encode(q[f])]
    return out

def main():
    progress('Step 2 started: exact half-turn-metric BFS over four labelled cross edges; scramble strings only.')
    t=time.perf_counter();table=transition_table()
    goals=np.array([[PAIR_INDEX[(f,b)] for b in range(6) if (f,b) in PAIR_INDEX] for f in range(6)],dtype=np.int32)
    distances=[];visited=[]
    for f in range(6):
        dist,n=bfs(table,goals[f]);assert n==190080
        assert dist[encode(goals[f])]==0 and dist[dist!=255].max()==8
        distances.append(dist);visited.append(n)
    distances=np.array(distances)
    tests=[]
    # Nonempty scrambles with solved crosses: U leaves D solved; Sune leaves D solved.
    for s, face, expected in [('U',0,1),('U',1,0),('R2',2,1),('R2',3,0),
                              ("R U R' U R U2 R'",1,0),('F F F F',4,0)]:
        got=int(face_lengths(moves(s),table,goals,distances)[face]);assert got==expected,(s,got)
        tests.append({'scramble':s,'face':FACES[face],'expected':expected,'actual':got,'pass':True})
    # Every one-step neighbor is distance 0 or 1; inverse transitions restore each state.
    for m in range(18):
        inv=(m//3)*3+2-m%3
        assert np.array_equal(table[inv,table[m]],np.arange(24))
        for f in range(6):assert distances[f,encode(table[m,goals[f]])] in (0,1)
    # Exhaustive local triangle identities verify BFS optimality, not just a few examples.
    rng=np.random.default_rng(20261001)
    for _ in range(1000):
        f=int(rng.integers(6));q=goals[f].copy()
        for m in rng.integers(18,size=25):q=table[m,q]
        d=int(distances[f,encode(q)])
        neigh=np.array([distances[f,encode(table[m,q])] for m in range(18)])
        assert np.all(np.abs(neigh.astype(int)-d)<=1)
        assert d==0 or neigh.min()==d-1
    g=pd.read_parquet(DERIVED/'scrambles.parquet')
    unique=g.scramble.unique();lookup={s:face_lengths(moves(s),table,goals,distances) for s in unique}
    lengths=np.array([lookup[s] for s in g.scramble])
    for j,f in enumerate(FACES):g['cross_length_'+f]=lengths[:,j]
    g['optimal_cross_all_six_faces']=lengths.min(1)
    g['optimal_cross_white_yellow']=lengths[:,:2].min(1)
    assert np.all(g.optimal_cross_all_six_faces<=g.optimal_cross_white_yellow)
    g.to_parquet(DERIVED/'cross.parquet',index=False)
    np.savez_compressed(DERIVED/'cross-pruning.npz',table=table,goals=goals,distances=distances)
    dump('cross.json',{'source_notice':NOTICE,'metric':'half-turn metric: U/U2/Uprime each one move; standard WCA orientation U=white, D=yellow',
      'positive_confirmation_times_read':False,'scheduled_scrambles':len(g),'unique_scramble_strings':len(unique),
      'bfs_visited_per_face':visited,'maximum_face_distance':8,'known_case_checks':tests,
      'inverse_move_checks':18,'random_bfs_triangle_and_descent_checks':1000,
      'all_six_face_counts':{str(k):int(v) for k,v in g.optimal_cross_all_six_faces.value_counts().sort_index().items()},
      'white_yellow_counts':{str(k):int(v) for k,v in g.optimal_cross_white_yellow.value_counts().sort_index().items()},
      'all_six_mean':float(g.optimal_cross_all_six_faces.mean()),'white_yellow_mean':float(g.optimal_cross_white_yellow.mean()),
      'elapsed_seconds':time.perf_counter()-t,'code_sha256':code_hashes()})
    progress(f'Step 2 complete: exact cross lengths for all {len(g):,} scheduled scrambles; six BFS tables each cover 190,080 states. Known solved-cross scrambles and inverse/optimality checks pass.')

if __name__=='__main__': main()
