"""Regel (23.10): tegnekvaliteten bytter bare når kameraet beveger seg. Hus som løfter seg skal ikke gi lavoppløst bilde."""
import re
from _felles import *
src = ''.join(open(os.path.join(ROT, 'src', f), encoding='utf8').read() for f in sorted(os.listdir(os.path.join(ROT, 'src'))) if f.endswith('.js'))
m = re.search(r'if\((.*?)\) sistBeveg=naa;', src)
ok = m is not None and 'husBeveger' not in m.group(1)
rapport('05_kvalitet_bare_kamera', ok, [f"sistBeveg settes av: {m.group(1) if m else 'ikke funnet'}"])
