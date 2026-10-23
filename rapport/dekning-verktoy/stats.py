import fitz, json, collections, colorsys, statistics, pickle
doc=fitz.open('pdf/brosjyre.pdf'); p=doc[0]
dr=p.get_drawings()
rows=[]
for i,d in enumerate(dr):
    r=d['rect']; f=d['fill']
    h,s,v=colorsys.rgb_to_hsv(*f)
    rows.append(dict(i=i,fill=tuple(round(x,3) for x in f),h=h,s=s,v=v,x0=r.x0,y0=r.y0,x1=r.x1,y1=r.y1,w=r.width,hh=r.height,area=r.width*r.height,n=len(d['items']),op=d.get('fill_opacity',1)))
pickle.dump(rows,open('soc/rapport/_tmp/rows.pkl','wb'))
# hue classes
def kl(r):
    h,s,v=r['h'],r['s'],r['v']
    if s<0.08:
        if v>0.9: return 'hvit'
        if v<0.12: return 'svart'
        if v<0.35: return 'moerkgraa'
        if v<0.7: return 'graa'
        return 'lysgraa'
    hd=h*360
    if hd<20 or hd>=340: return 'roed'
    if hd<45: return 'oransje/brun'
    if hd<70: return 'gul'
    if hd<170: return 'groenn'
    if hd<260: return 'blaa/turkis'
    return 'lilla/rosa'
cnt=collections.Counter(); areas=collections.defaultdict(list)
for r in rows:
    k=kl(r); cnt[k]+=1; areas[k].append(r['area'])
for k,v in cnt.most_common():
    a=areas[k]; print(f"{k:14s} n={v:5d} med_area={statistics.median(a):8.1f} max={max(a):10.0f} sum={sum(a):10.0f}")
# opacity
print(collections.Counter(round(r['op'],2) for r in rows).most_common(8))
