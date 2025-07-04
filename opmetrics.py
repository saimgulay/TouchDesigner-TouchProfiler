# Full, complete script for performance evaluation
# This version writes its output to a separate DAT named 'cookMetrics'

num_samples    = 10
delay_frames   = 12    # ~0.2s @60FPS
collected_data = []
_sample_frame  = 0

def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Settings')
    page.appendOP('Targetcomp', label='Container to Analyse').default = 'project1'
    page.appendPulse('Sample',     label='Start Sampling')
    return

def onCook(scriptOp):
    global _sample_frame, collected_data
    
    # Define the output DAT
    output_dat = op('cookMetrics')
    if not output_dat:
        # If cookMetrics doesn't exist, you can stop or write the error to the script op itself
        # For now, let's just prevent further cooking.
        return

    root = op(scriptOp.par.Targetcomp.eval())
    if not root:
        output_dat.clear()
        output_dat.appendRow(['Error', f"Could not find '{scriptOp.par.Targetcomp.eval()}'"])
        return

    # kick off sampling
    if scriptOp.par.Sample.eval() and _sample_frame == 0:
        collected_data = []
        _sample_frame = 1

    # while sampling
    if _sample_frame > 0:
        collected_data.append(_collect_metrics(root))
        if _sample_frame < num_samples:
            _sample_frame += 1
            scriptOp.run('me.cook(force=True)', delayFrames=delay_frames)
            return
        else:
            # Pass the output DAT to the analysis function
            _analyse_and_display(output_dat)
            _sample_frame = 0
            return

    return

def _collect_metrics(root):
    data = {}
    def recurse(o):
        if o.name.startswith('_') or o.name.startswith('sys'):
            return
        try:
            o.cook(force=True)
        except:
            pass
        data[o.path] = {
            'cookTime':        getattr(o, 'cookTime', 0),
            'gpuCookTime':     getattr(o, 'gpuCookTime', 0),
            'cookAbsFrame':    getattr(o, 'cookAbsFrame', 0),
            'cookCount':       getattr(o, 'cookCount', 0),
            'memoryUsed':      getattr(o, 'memoryUsed', 0),
            'childrenCookTime':getattr(o, 'childrenCookTime', 0),
        }
        for c in o.children:
            recurse(c)
    recurse(root)
    return data

def _analyse_and_display(output_dat): # Takes the target DAT as an argument
    import math

    agg = {}
    for snap in collected_data:
        for path, vals in snap.items():
            e = agg.setdefault(path, {
                'times':[], 'gpus':[], 'mems':[], 'children':[],
                'lastFrame':0, 'lastCount':0
            })
            e['times'].append(vals['cookTime'])
            e['gpus'].append(vals['gpuCookTime'])
            e['mems'].append(vals['memoryUsed'])
            e['children'].append(vals['childrenCookTime'])
            e['lastFrame'] = vals['cookAbsFrame']
            e['lastCount'] = vals['cookCount']

    results = []
    for path, d in agg.items():
        if not d['times']: continue
        
        avgT = sum(d['times'])/len(d['times'])
        stdT = math.sqrt(sum((t-avgT)**2 for t in d['times'])/len(d['times']))
        avgG = sum(d['gpus'])/len(d['gpus'])
        avgM = sum(d['mems'])/len(d['mems'])
        avgC = sum(d['children'])/len(d['children'])
        score = avgT * (1 + stdT)
        results.append((score, path, avgT, stdT, avgG, d['lastFrame'], d['lastCount'], avgM, avgC))

    results.sort(key=lambda x: x[0], reverse=True)

    output_dat.clear() # Clear the target DAT
    headers = [
        'Score','Path','AvgCookTime','StdDevCookTime',
        'AvgGpuCookTime','LastCookFrame','LastCookCount',
        'AvgMemoryUsed','AvgChildrenCookTime'
    ]
    output_dat.appendRow(headers) # Write headers to the target DAT

    for r in results[:10]:
        # Write results to the target DAT
        output_dat.appendRow([ round(r[0],4), r[1], round(r[2],4), round(r[3],4),
                             round(r[4],4), r[5], r[6],
                             round(r[7],2), round(r[8],4) ])