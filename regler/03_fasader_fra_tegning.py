"""Regel (Vegar): vinduer og dører skal følge kvartaltegningene. Teller hvor mange hus som har det."""
from _felles import *
b = data('bygg'); fra = [i for i, x in gamleby(b) if x.get('fasade_kilde') == 'kvartaltegning']; antatt = [i for i, x in gamleby(b) if x.get('fasade_kilde') != 'kvartaltegning' and not x.get('skjul')]
rapport('03_fasader_fra_tegning', not antatt, [f"{len(fra)} hus med fasade fra tegning, {len(antatt)} antatt (må kvalitetssikres kvartal for kvartal)", f"- antatt: {', '.join(map(str, antatt))}"])
