"""Regel 49 (OPPGAVE5): hvert faktum i kilder/bygg-innhold.json som har en verdi, må ha minst én kilde med adresse og
lesedato. Innholdet (navn/byggeår/historie/bruk i dag) er det kartet viser på huskortet, og ingenting skal vises uten at
det kan føres tilbake til en lest kilde — ellers er det gjetning. Rød = publisering stoppes i ALLE moduser (sperren i
publiser.sh leser denne regelen, som regel 48). Tomt felt (verdi null/tom) er greit: da vises ingenting, og ingen kilde kreves.

Leservei: fakta leses gjennom datalaget (datalag.innhold_hus()), samme fil og samme vei som kartet fylles fra, så sjekken
gjelder nøyaktig det kartet kan komme til å vise.
"""
import os, sys
from _felles import rapport

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FELT = ('navn', 'byggeaar', 'historie', 'bruk_i_dag')


def har_verdi(f):
    """Et faktum har verdi når feltet er et objekt med en ikke-tom verdi. Alt annet (null, manglende) er tomt."""
    return isinstance(f, dict) and f.get('verdi') not in (None, '', [], {})


def mangler(kilder):
    """Grunner til at kildelista ikke holder: ingen kilde, eller en kilde uten adresse eller uten dato."""
    if not isinstance(kilder, list) or not kilder:
        return 'ingen kilde'
    for k in kilder:
        if not isinstance(k, dict) or not str(k.get('adresse') or '').strip():
            return 'kilde uten adresse'
        if not str(k.get('dato') or '').strip():
            return 'kilde uten dato'
    return None


def main():
    if ROT not in sys.path:
        sys.path.insert(0, ROT)
    import datalag
    hus = datalag.innhold_hus()

    feil = []       # (id, felt, grunn)
    fakta = 0
    for id_, h in hus.items():
        for felt in FELT:
            f = h.get(felt)
            if not har_verdi(f):
                continue
            fakta += 1
            grunn = mangler(f.get('kilder'))
            if grunn:
                feil.append((id_, felt, grunn))

    ok = not feil
    linjer = []
    if ok:
        linjer.append(f"{fakta} fakta i {len(hus)} hus, alle med kilde + dato")
    else:
        linjer.append(f"{len(feil)} fakta med verdi uten gyldig kilde (av {fakta} fakta i {len(hus)} hus)")
        for id_, felt, grunn in sorted(feil):
            linjer.append(f"- {id_} {felt}: {grunn}")

    return rapport('49_innhold_kildefestet', ok, linjer)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
