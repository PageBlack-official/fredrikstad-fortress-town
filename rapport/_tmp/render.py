"""Tegn et utvalg av fyllbaner fra side 1 til PNG. Bruk: render.py ut.png zoom 'uttrykk' [bg]"""
import fitz, sys, colorsys, pickle
rows=pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'rows.pkl'),'rb'))
doc=fitz.open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','..','..','pdf','brosjyre.pdf')); p=doc[0]; dr=p.get_drawings()
ut=sys.argv[1]; zoom=float(sys.argv[2]); expr=sys.argv[3]; bg=sys.argv[4] if len(sys.argv)>4 else 'white'
new=fitz.open(); pg=new.new_page(width=p.rect.width,height=p.rect.height)
if bg=='grey':
    sh=pg.new_shape(); sh.draw_rect(pg.rect); sh.finish(fill=(0.6,0.6,0.6),color=None); sh.commit()
sel=[r for r in rows if eval(expr, {}, dict(r, **{'hd':r['h']*360}))]
print('valgt',len(sel))
sh=pg.new_shape()
for r in sel:
    d=dr[r['i']]
    for it in d['items']:
        if it[0]=='l': sh.draw_line(it[1],it[2])
        elif it[0]=='c': sh.draw_bezier(it[1],it[2],it[3],it[4])
        elif it[0]=='re': sh.draw_rect(it[1])
        elif it[0]=='qu': sh.draw_quad(it[1])
    sh.finish(fill=d['fill'],color=None,even_odd=d.get('even_odd',False),closePath=d.get('closePath',True))
sh.commit()
pix=pg.get_pixmap(matrix=fitz.Matrix(zoom,zoom),alpha=False); pix.save(ut)
