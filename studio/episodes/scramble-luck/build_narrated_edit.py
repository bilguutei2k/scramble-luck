"""Build the pre-lock edit from actual Kokoro written-word timings.

Run after studio/tools/narrate.py. Keeps every script word once, splits only
cached PCM, and places each named state on its spoken word.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent
sys.path.insert(0, str(EP.parents[1] / 'tools'))
from assemble import slice_line, sequence_plans

PUNCT = '\"\'“”‘’.,:;?!()'


def clean(word):
    return word.strip(PUNCT).lower()


WORD_CUES = {
    's01': ['A', 'WIRED', 'Ruwix', 'Yusheng', 'narrower'],
    's02': ['scramble', 'CFOP', 'cross', 'PLL', 'average'],
    's03': ['reconstruction', 'skip', 'adjustment', 'other'],
    's04': ['diagram', 'execute', 'peers'],
    's05': ['WCA', 'held', '5,017', '306,155', '3,313'],
    's06': ['row', 'compare', 'favorable', 'remove', 'noise'],
    's07': ['select', 'remove', 'geometrically', 'separate'],
    's08': ['Before', 'failed', 'amendment', 'passed', 'fixed-selection'],
    's09': ['line', '1.0198', '95%', '2%', 'fails'],
    's10': ['4.7%', '597', 'below', 'similar', 'geometry'],
    's11': ['slot', 'extra', 'failures', 'positive', 'remaining'],
    's12': ['aggregate', '2%', 'rule', 'linked'],
    'short-a': ['A', '2%', '1.0198', '95%', 'rule', 'doesn\'t'],
    'short-b': ['Max', 'shortcut', 'excluding', 'reconstruction'],
    'short-c': ['scramble', 'shared', 'extra', 'successful'],
}


def state_cues(page, info, lines):
    """Match exact CUES substrings, then choose the stressed written word."""
    prefix = page[:3] if page.startswith('s0') or page.startswith('s1') else page[:-5]
    targets = WORD_CUES[prefix]
    result = []
    for state, target in zip(info['states'], targets):
        found = None
        for i, line in enumerate(lines):
            at = line['written'].find(state['cue'])
            if at < 0:
                continue
            first = len(line['written'][:at].split())
            last = first + len(state['cue'].split())
            options = [j for j in range(first, last) if clean(line['words'][j]['w']) == clean(target)]
            if not options:
                # The payoff word may follow the cue's introductory substring.
                options = [j for j in range(first, len(line['words'])) if clean(line['words'][j]['w']) == clean(target)]
            if not options:
                raise ValueError((page, state['id'], target))
            found = dict(state=state, index=i, word_index=options[0])
            break
        if found is None:
            raise ValueError((page, state['cue']))
        result.append(found)
    assert len(result) == len(info['states'])
    assert [(x['index'], x['word_index']) for x in result] == sorted((x['index'], x['word_index']) for x in result)
    return result


def split(line):
    count = len(line['words'])
    if line['duration'] <= 12.6:
        return [(0, count)]
    parts = math.ceil(line['duration'] / 11.5)
    boundaries = [0]
    for k in range(1, parts):
        target = line['duration'] * k / parts
        options = range(boundaries[-1] + 3, count - (parts-k)*3)
        def cost(j):
            t = (line['words'][j-1]['end'] + line['words'][j]['start']) / 2
            punctuation = bool(re.search(r'[.,;:?!][”\']?$', line['words'][j-1]['w']))
            return abs(t-target) - (.8 if punctuation else 0)
        boundaries.append(min(options, key=cost))
    boundaries.append(count)
    return list(zip(boundaries, boundaries[1:]))


def word_gates(shot, page, lines, i, a, b):
    """Do not show fresh interval endpoints before their spoken numbers."""
    rules = []
    key = 'primary.R_geometric_person_year'
    if page.startswith('s09'):
        rules += [(0, '1.10', '.sl-state[data-state="line"] .sl-reference'),
                  (0, '10%', '.sl-state[data-state="line"] .caption'),
                  (2, 'below', '.sl-state[data-state="interval"] .caption')]
        interval_id, interval_line = 'interval', 1
    elif page == 'short-a.html':
        rules += [(2, 'rule', '.sl-reference')]
        interval_id, interval_line = 'interval', 1
    else:
        interval_id = None
    if page.startswith('s10'):
        root = '.sl-state[data-state="variance"] '
        rules += [(0, '4.7%', root+'.number'),
                  (0, 'interval', root+'.label:has([data-value-key*="interval_95"])')]
    if page == 'short-b.html':
        root = '.sl-state[data-state="skip"] '
        rules += [(0, 'PLL', root+'.ft-measure-card:first-child .ft-measure-content'),
                  (0, 'alignment', root+'.ft-measure-card:last-child .ft-measure-content'),
                  (0, 'PLL', root+'.sl-pending-skip', True),
                  (0, 'alignment', root+'.sl-pending-align', True)]
    if interval_id:
        root = '.sl-state[data-state="'+interval_id+'"] '
        rules += [(interval_line, '1.0164', root+'[data-value-key="'+key+'.interval_95[0]"]'),
                  (interval_line, '1.0231', root+'[data-value-key="'+key+'.interval_95[1]"]'),
                  (interval_line, '1.0231', root+'.sl-interval')]
    if page == 'short-a.html':
        rules = [(li, word, selector.replace('[data-value-key="'+key+'.interval_95[0]"]', '.sl-endpoint-low').replace('[data-value-key="'+key+'.interval_95[1]"]', '.sl-endpoint-high')) for li, word, selector in rules]
    reveals = []
    for rule in rules:
        line_index, target, selector = rule[:3]
        hide_after = len(rule)>3 and rule[3]
        j = next(j for j,w in enumerate(lines[line_index]['words']) if clean(w['w'])==clean(target))
        if line_index > i or (line_index == i and j >= b):
            if not hide_after:
                reveals.append(dict(selector=selector,hidden=True))
        elif line_index == i and a <= j < b:
            nth = sum(clean(w['w'])==clean(target) for w in lines[i]['words'][a:j+1])
            reveals.append(dict(selector=selector,line=0,word=lines[i]['words'][j]['w'],nth=nth,**({'hide_after':True} if hide_after else {})))
        elif hide_after:
            reveals.append(dict(selector=selector,hidden=True))
    if reveals:
        shot['reveals'] = reveals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--narration', type=Path, default=EP/'renders/audio/narration.json')
    parser.add_argument('--output', type=Path, default=EP/'EDIT.json')
    args = parser.parse_args()
    narration = json.loads(args.narration.read_text())
    cues = json.loads((EP/'scenes/CUES.json').read_text())
    edit = dict(status='locked', about='Owner-approved 2026-10-03; unchanged narration; actual Kokoro word timings; verified claims.',
                voice='af_heart', timing='Every named state lands on its spoken written word; stable snapshots, hard cuts, strict captions and sample-contiguous cached PCM fragments.',
                gap=.45, lead=.4, tail=.9, wipe=.45, bridge_word_ranges=True,
                strict_captions=True, audio_true_peak=-1.5, calibrate_loudness=True,
                settled_visuals=True, deliverables={})
    for name in ['film', 'short-a', 'short-b', 'short-c']:
        pages = [p for p in cues['scenes'] if p.startswith('s') and not p.startswith('short')] if name=='film' else [name+'.html']
        shots = []
        for page in pages:
            info = cues['scenes'][page]
            key = page[:3].upper() if name=='film' else 'Short '+name[-1].upper()
            lines = narration['scenes'][key]['lines']
            events = state_cues(page, info, lines)
            active = info['states'][0]
            def hold_t(state):
                next_at = next((s['at'] for s in info['states'] if s['at']>state['at']), info['duration'])
                return next_at-.05
            for i, line in enumerate(lines):
                ranges = split(line)
                for a,b in ranges:
                    spoken = slice_line(line,[a,b])
                    shot = dict(scene=page[:-5], bg='night' if page.startswith(('s01','s12')) else 'paper',
                                **{'in':'cut'}, lines=[key,[i]], word_ranges=[[a,b]],
                                about=key+' · line '+str(i)+' · words '+str(a)+'–'+str(b), cues=[])
                    if not shots and name!='film':
                        shot['lead'] = .15
                    # One line may cross several states; keep the preceding chart
                    # until the next word, then jump over the designed clock hold.
                    selected = [e for e in events if e['index']==i and a<=e['word_index']<b]
                    initial = hold_t(active) if active['at'] else 0
                    shot['cues'].append(dict(t=initial,line=0))
                    for event in selected:
                        state = event['state']; w = line['words'][event['word_index']]['w']
                        nth = sum(clean(x['w'])==clean(w) for x in line['words'][a:event['word_index']+1])
                        cue = dict(t=state['at'],line=0,word=w,nth=nth)
                        if state['at'] < initial:
                            # Initial state is already established at the cut.
                            cue['t'] = initial
                        if state['at'] > initial:
                            cue['jump_from'] = initial
                        shot['cues'].append(cue)
                        active = state
                        initial = hold_t(state)
                    next_at = next((s['at'] for s in info['states'] if s['at']>active['at']), info['duration'])
                    shot['end_t'] = next_at-.05
                    word_gates(shot, page, lines, i, a, b)
                    # Full-frame shot pacing; adjacent fragments are bridged by
                    # assemble.py, so never extend a fragment with silence.
                    if len(ranges)==1:
                        shot['tail'] = max(.9, 6-(shot.get('lead',.4)+spoken['duration']))
                    shots.append(shot)
        edit['deliverables'][name] = dict(format='landscape' if name=='film' else 'vertical',
                                        title='About 2% Longer' if name=='film' else name,shots=shots)
    args.output.write_text(json.dumps(edit,indent=2)+'\n')
    for name,spec in edit['deliverables'].items():
        plans = sequence_plans(spec['shots'],narration,edit)
        print(name, len(plans), 'shots', round(sum(p['duration'] for p in plans),3), 'seconds',
              'shot range', round(min(p['duration'] for p in plans),3),round(max(p['duration'] for p in plans),3))


if __name__ == '__main__':
    main()
