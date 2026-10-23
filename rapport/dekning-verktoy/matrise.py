import json, glob, pickle, numpy as np, collections
M=np.load('pdf/affin2.npy'); K=72/300
A=M[:2,:]; t=M[2,:]; Ainv=np.linalg.inv(A)
def m2pt(xy): return (np.array([xy[0],xy[1]])@A+t)*K
def pt2m(pt): return (np.array(pt)/K - t)@Ainv
D={f:json.load(open(f'soc/data/{f}.json')) for f in ['bygg','traer','murer','gjerder','porter','broer','statue','legende','gardsrom','brostein','veier','gront','voller','vann']}
rows=pickle.load(open('soc/rapport/_tmp/rows.pkl','rb'))
TRE={(0.386,0.574,0.439),(0.323,0.493,0.376),(0.29,0.45,0.342),(0.304,0.468,0.356),(0.342,0.518,0.395),(0.313,0.481,0.366)}
trykk_tre=[pt2m(((r['x0']+r['x1'])/2,(r['y0']+r['y1'])/2)) for r in rows if r['fill'] in TRE and r['area']>150]
trykk_mark=[pt2m(((r['x0']+r['x1'])/2,(r['y0']+r['y1'])/2)) for r in rows if r['fill']==(0.221,0.216,0.222) and 190<r['area']<230]
trykk_ikon=[pt2m(((r['x0']+r['x1'])/2,(r['y0']+r['y1'])/2)) for r in rows if r['fill']==(1.0,1.0,1.0) and 14<r['w']<17 and abs(r['w']-r['hh'])<1.5]
print('trykk: trær',len(trykk_tre),'markører',len(trykk_mark),'ikoner',len(trykk_ikon))
b=D['bygg']
def cen(p): return np.mean(p,axis=0)
regioner=[]
for f in sorted(glob.glob('kvartal/ut/kobling-*.json')):
    k=json.load(open(f)); idx=k['kvartal']
    pts=np.array([p for i in idx for p in b[i]['p']]); mn=pts.min(0)-10; mx=pts.max(0)+10
    u=json.load(open(f.replace('kobling-',''))); ntak=sum(1 for x in u['fasader'] if x['typ']=='tak')
    regioner.append((k['navn'],mn,mx,ntak,'kvartaltegning'))
# Tøihuset
p=np.array(b[5]['p']); regioner.append(('Tøihuset (19)',p.min(0)-12,p.max(0)+12,None,'bare trykk'))
# Vest: 11,12,13,14
p=np.array([q for i in (14,1,2,265) for q in b[i]['p']]); regioner.append(('Vest: 11–14',p.min(0)-12,p.max(0)+12,None,'bare trykk'))
# ekstra regioner definert i trykk-pt (bbox) -> modell
def reg_pt(navn,x0,y0,x1,y1):
    c=np.array([pt2m((x,y)) for x,y in [(x0,y0),(x1,y0),(x0,y1),(x1,y1)]]); regioner.append((navn,c.min(0),c.max(0),None,'bare trykk'))
reg_pt('Isegran',0,60,330,330)
reg_pt('Havn/Vindebroen (25–28)',870,330,1060,450)
reg_pt('Sør: voll 17–18,21–22',250,560,720,760)
reg_pt('Nord/øst-vollen (33–34)',520,0,1190,260)
def inn(xy,mn,mx): return mn[0]<=xy[0]<=mx[0] and mn[1]<=xy[1]<=mx[1]
ut=[]
for navn,mn,mx,ntak,kilde in regioner:
    r=dict(navn=navn,kilde=kilde,tak_tegning=ntak)
    r['m_bygg']=sum(1 for x in b if x['p'] and not x.get('skjul') and inn(cen(x['p']),mn,mx))
    r['m_traer']=sum(1 for x in D['traer'] if inn(x[:2],mn,mx))
    r['m_murer']=sum(1 for x in D['murer'] if any(inn(q,mn,mx) for q in x['p']))
    r['m_gjerder']=sum(1 for x in D['gjerder'] if any(inn(q,mn,mx) for q in x))
    r['m_porter']=sum(1 for x in D['porter'] if inn(cen(b[x['bygg']]['p']),mn,mx))
    r['m_broer']=sum(1 for x in D['broer'] if any(inn(q,mn,mx) for q in x['p']))
    r['m_statue']=sum(1 for x in D['statue'] if inn(x['xy'],mn,mx))
    r['m_legende']=sum(1 for x in D['legende'] if inn(x['xy'],mn,mx))
    r['m_gardsrom']=sum(1 for x in D['gardsrom'] if inn(cen(x['p']),mn,mx))
    r['m_brostein']=sum(1 for x in D['brostein'] if inn(x,mn,mx))
    r['m_veier']=sum(1 for x in D['veier'] if inn(cen(x['p']),mn,mx))
    r['m_gront']=sum(1 for x in D['gront'] if any(inn(q,mn,mx) for q in x['p']))
    r['m_voller']=sum(1 for x in D['voller'] if any(inn(q,mn,mx) for q in x))
    r['t_traer']=sum(1 for x in trykk_tre if inn(x,mn,mx))
    r['t_mark']=sum(1 for x in trykk_mark if inn(x,mn,mx))
    r['t_ikon']=sum(1 for x in trykk_ikon if inn(x,mn,mx))
    r['bbox_m']=[round(float(v)) for v in (*mn,*mx)]
    p0=m2pt(mn); p1=m2pt(mx); p2=m2pt((mn[0],mx[1])); p3=m2pt((mx[0],mn[1])); P=np.array([p0,p1,p2,p3])
    r['bbox_pt']=[round(float(v)) for v in (*P.min(0),*P.max(0))]
    ut.append(r)
json.dump(ut,open('soc/rapport/_tmp/matrise.json','w'),indent=1,ensure_ascii=False)
keys=['navn','tak_tegning','m_bygg','t_traer','m_traer','t_mark','m_legende','t_ikon','m_murer','m_gjerder','m_porter','m_broer','m_statue','m_gardsrom','m_brostein','m_veier','m_gront','m_voller']
print('\t'.join(keys))
for r in ut: print('\t'.join(str(r[k]) for k in keys))
# totals inside print extent (whole map area pt 0..1190 x 0..700)
c=np.array([pt2m((x,y)) for x,y in [(0,0),(1190,0),(0,700),(1190,700)]]); mn=c.min(0); mx=c.max(0)
print('kartutsnitt modell bbox', mn, mx)
print('modell innenfor kartet: bygg',sum(1 for x in b if x['p'] and not x.get('skjul') and inn(cen(x['p']),mn,mx)),'traer',sum(1 for x in D['traer'] if inn(x[:2],mn,mx)))
