"""Regel (23.10, lagt om 06.11): det som er publisert, er den versjonen vi tror. Grunn: publiser.sh stoppet stille 23.10 (gh-pages fantes
lokalt), og Pages stod på v27 hele kvelden mens vi målte ytelse på «v28».
Før 06.11 sjekket regelen også artefaktbygget (../publiser/gamle-fredrikstad.html), kartet som Claude-artefakt. Den kanalen er lagt ned
(siden 05.11 publiseres alt med publiser.sh til GitHub Pages), så regelen ble rød for en fil som ikke skal finnes lenger. Nå sjekkes
de to adressene som faktisk er ute:
- forsiden og /prove/: «Versjon N» i meta-beskrivelsen = VERSJON;
- <meta name="kilde">: en commit som finnes i repoet og ligger i historikken til det vi står på (ikke et bygg fra en annen gren).
  Forsider bygd før 05.11 har ikke kilde-merket; det står som merknad, ikke feil.
At /prove/ står på en eldre kilde enn den vi sjekker, er normalt før publisering og står som merknad. publiser.sh venter selv til
/prove/ viser den nye kilden etter publisering, og stopper med feil om den ikke gjør det (det er den stille feilen fra 23.10)."""
import os, re, subprocess, urllib.request
from _felles import *
PAGES = 'https://pageblack-official.github.io/fredrikstad-fortress-town/'
onsket = open(os.path.join(ROT, 'VERSJON')).read().strip()
def git(*a): return subprocess.run(['git', '-C', ROT, *a], capture_output=True, text=True)
naa = git('log', '-1', '--format=%h', '--', 'src', 'data', 'regler', 'bygg.py', 'datalag.py', 'assets').stdout.strip()
linjer = []; ok = True
def hent(url):
    with urllib.request.urlopen(urllib.request.Request(url + '?n=' + str(os.getpid()), headers={'Cache-Control': 'no-cache', 'User-Agent': 'sot-regel-09'}), timeout=20) as r:
        return r.read().decode('utf8', 'replace')
for navn, url in (('forsiden', PAGES), ('/prove/', PAGES + 'prove/')):
    try: html = hent(url)
    except Exception as e:
        linjer.append(f'- {navn}: kunne ikke hentes ({e})'); ok = False; continue
    m = re.search(r'Versjon (\d+(?:\.\d+)?)\.', html); v = m.group(1) if m else None
    k = re.search(r'<meta name="kilde" content="([0-9a-f]{7,40})"', html); k = k.group(1) if k else None
    vok = v == onsket; ok &= vok
    t = f'- {navn}: versjon {v} (ønsket {onsket})'
    if k is None:
        if navn == '/prove/': t += ', mangler kilde-merket'; ok = False
        else: t += ', bygd før kilde-merket (05.11)'
    elif git('cat-file', '-e', k + '^{commit}').returncode != 0:
        t += f', kilde {k} finnes ikke i repoet'; ok = False
    elif git('merge-base', '--is-ancestor', k, 'HEAD').returncode != 0:
        t += f', kilde {k} er ikke i historikken vi står på'; ok = False
    else:
        t += f', kilde {k}' + ('' if k == naa or navn == 'forsiden' else f' (merknad: eldre enn {naa}, venter publisering)')
    linjer.append(t)
rapport('09_publisert', ok, linjer)
