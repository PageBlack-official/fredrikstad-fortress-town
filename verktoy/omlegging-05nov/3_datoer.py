"""Omleggingen 05.11, steg 3: datoene ut av kommentarene. Kommentaren beholder hvorfor (og Vegars ord når de er grunnen);
når og i hvilken rekkefølge står i CHANGELOG.md under «Kommentarhistorikk 23.10–05.11», med fil og linje slik de stod."""
import re, os, json
ROT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
orden=json.load(open(os.path.join(ROT,'verktoy','omlegging-05nov','orden.json')))
D=r'\d{1,2}\.(?:10|11)'
TID=r'(?: kveld| kl\. ?\d{1,2}[.:]\d\d| \d\d:\d\d)?'
regler=[
  (re.compile(r'\(\s*'+D+TID+r'\)\s*'), ''),                            # «(05.11) »
  (re.compile(r'\((?:Vegar )?'+D+TID+r', '), '('),                      # «(05.11, Vegar: …» → «(Vegar: …»
  (re.compile(r', (?:Vegar )?'+D+TID+r'\)'), ')'),                      # «…, 24.10)» → «…)»
  (re.compile(r'\((Vegar|Vegars Chrome|natt/[a-z]+|oppdrag \d+|teknikk \d+|avvik A\d+|regel \d+) '+D+TID+r'\)'), r'(\1)'),
  (re.compile(r'\b(Vegar|Vegars Chrome|Vegars iPhone) '+D+TID+r'\b'), r'\1'),
  (re.compile(r'\b(avvik A\d+|natt/[a-z]+|oppdrag \d+|regel \d+), '+D+TID+r'\b'), r'\1'),
  (re.compile(r'\b'+D+TID+r', (avvik A\d+|natt/[a-z]+|oppdrag \d+|Kaserna|Tøihuset)\b'), r'\1'),
  (re.compile(r'(//\s*)'+D+TID+r':\s*'), r'\1'),                       # «// 29.10: …»
  (re.compile(r'(//\s*)'+D+TID+r' \('), r'\1('),
]
hist=[]; endret=0
for f in orden:
    p=os.path.join(ROT,'src',f); linjer=open(p,encoding='utf8').read().split('\n')
    for i,l in enumerate(linjer):
        m=re.search(r'(//|/\*).*$',l)
        if not m or not re.search(r'\b'+D+r'\b',m.group(0)): continue
        hist.append(f'- {f}:{i+1}: {m.group(0).strip()}')
        k=m.group(0)
        for r,b in regler: k=r.sub(b,k)
        if k!=m.group(0): linjer[i]=l[:m.start()]+k; endret+=1
    open(p,'w',encoding='utf8').write('\n'.join(linjer))
rest=[]
for f in orden:
    for i,l in enumerate(open(os.path.join(ROT,'src',f),encoding='utf8').read().split('\n')):
        m=re.search(r'(//|/\*).*$',l)
        if m and re.search(r'\b'+D+r'\b',m.group(0)): rest.append(f'{f}:{i+1}: {m.group(0)[:200]}')
cl=os.path.join(ROT,'CHANGELOG.md'); s=open(cl,encoding='utf8').read()
blokk='\n## Kommentarhistorikk 23.10–05.11 (flyttet ut av koden 05.11)\nKommentarene i src/ sier nå hvorfor koden er slik. Datoene og rekkefølgen stod slik i kommentarene før omleggingen (fil:linje i 3b93557 etter steg 1–2):\n'+'\n'.join(hist)+'\n'
open(cl,'w',encoding='utf8').write(s.rstrip('\n')+'\n'+blokk)
print('kommentarer med dato:',len(hist),'endret:',endret,'dato igjen:',len(rest)); print('\n'.join(rest))
