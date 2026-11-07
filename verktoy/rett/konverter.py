"""ute/el-*.json + vegger.json → rett-<navn>.json (for verktoy/fasade_rett.py). godkjent settes bare via godkjent.txt (øyekontroll).
    python3 konverter.py <vegger.json> <ut.json>"""
import json,glob,sys
V=json.load(open(sys.argv[1]))
G=set(open('godkjent.txt').read().split()) if glob.glob('godkjent.txt') else set()
ut=[]
for f in sorted(glob.glob('ute/el-*.json')):
    for r in json.load(open(f)):
        if not r.get('ok'): continue
        v=V[r['bilde']]
        ut.append({'bilde':r['bilde'],'id':v['id'],'vegg':v['vegg'],'venstre':v['venstre'],'hoyre':v['hoyre'],'lengde':v['lengde'],'h':v['h'],
                   'elementer':r['elementer'],'telling':r.get('telling',''),'godkjent':r['bilde'] in G})
json.dump(ut,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(len(ut),'fasader,',sum(u['godkjent'] for u in ut),'godkjent')
