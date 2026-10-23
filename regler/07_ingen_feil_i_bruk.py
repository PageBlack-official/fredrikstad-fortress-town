"""Regel (23.10): kartet skal brukes uten én eneste JS-feil. Intro, klikk, Esc, styreflate, hjul, dobbeltklikk og musedra kjøres (interaksjon-test),
og én feil er nok til rødt. Grunn: en feil inni render() gjør at laget vårt ikke tegnes det bildet, og kartet blinker papirhvitt
(23.10: «const grunn» tilordnet på nytt i oppdaterSol ga hvitt blink ved hver bevegelse på Mac og mobil)."""
import subprocess, os, re
from _felles import *
r = subprocess.run(['node', os.path.join(ROT, 'verktoy', 'interaksjon-test.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html')], capture_output=True, text=True)
ut = r.stdout.strip().split('\n')
feil = [l for l in ut if l.startswith('feil')]
ok = r.returncode == 0 and feil == ['feil []']
rapport('07_ingen_feil_i_bruk', ok, ['- ' + l for l in ut[-8:]])
