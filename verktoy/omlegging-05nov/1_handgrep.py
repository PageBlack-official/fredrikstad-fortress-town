"""Omleggingen 05.11 (Vegar: «fiks spagettien»), steg 1: det som må gjøres for hånd før modulene kan lages maskinelt.
Kjøres én gang på kilden fra 3b93557. Kvalitet og tegnetilstand får hver sin eier (kvalitet.js, tilstand.js); fit flyttes dit post bor."""
import os
ROT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); S=lambda f: os.path.join(ROT,'src',f)
def ed(f, pairs):
    s=open(S(f),encoding='utf8').read()
    for a,b in pairs:
        assert s.count(a)==1, (f,a[:60],s.count(a)); s=s.replace(a,b)
    open(S(f),'w',encoding='utf8').write(s)
s=open(S('00_oppsett.js'),encoding='utf8').read().split('\n')
s=[l for l in s if not l.startswith('let skalaStille=1, skalaMaskin=1;') and not l.startswith('function beregnSkala(){') and l not in ('function fit(){ post.size(); }',"map.on('resize',fit);")]
open(S('00_oppsett.js'),'w',encoding='utf8').write('\n'.join(s))
ed('01_etterbehandling.js',[])
s=open(S('01_etterbehandling.js'),encoding='utf8').read().rstrip('\n')+"\n// lerretet har endret størrelse: målene til etterbehandlingen følger (fra 00, der post ennå ikke fantes)\nfunction fit(){ post.size(); }\nmap.on('resize',fit);\n"
open(S('01_etterbehandling.js'),'w',encoding='utf8').write(s)
ed('02_lys.js',[('let skyggeSkitten=true, kameraBeveget=true;','let kameraBeveget=true;')])
s=open(S('14_speilinger-i-vannet.js'),encoding='utf8').read()
a=s.index('// ytelse: måler bildefrekvensen'); b=s.index('function speilStyrke()'); s=s[:a]+s[b:]
s=s.replace('let ssStille=4;\n','')
s=s.replace('let speilInn=0, speilFrisk=false, sistBeveg=0, sistTegnet=0, fullTegnet=false, aoStille=14; const _sisteKam','const _sisteKam')
a=s.index('// Måler tiden vår egen tegning'); e="if(Q.get('nivaa')) settNivaa(+Q.get('nivaa'));\n"; b=s.index(e)+len(e); s=s[:a]+s[b:]
s=s.replace('const clock=new THREE.Clock(); let _synlig=false;','const clock=new THREE.Clock();').replace('const Q=Q0; let introDone=false;','const Q=Q0;')
open(S('14_speilinger-i-vannet.js'),'w',encoding='utf8').write(s)
ed('15_loop.js',[('if(perfOnsket>perfNivaa && stille && !fingerNede) settNivaa(perfOnsket);','byttNivaaNaarStille(stille, fingerNede);')])
print('handgrep ok')
