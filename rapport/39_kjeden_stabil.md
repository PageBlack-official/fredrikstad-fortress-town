# 39_kjeden_stabil: FEIL

kjeden feilet i kopien
ferdig: 345 hus
OK   -I rapport/hoyder/legg_inn.py            202 hus fått målt høyde og takhelning
OK   verktoy/vinduer_regler.py                117 antatte hus fikk vind etter reglene: 788 vinduer, 32 dører (før: 817 elementer); 42 uten noe (lave eller inneklemte)
OK   verktoy/sv_kobling.py                    332 observasjoner, 78 peker ikke på huset (48 hus)
OK   verktoy/streetview_fasader.py            55 hus endret, 95 fasithus sammenlignet (52 med avvik), 130 hoppet over
OK   verktoy/streetview_farger.py             104 vegger fra Street View 2016 eller senere
FEIL verktoy/fasade_tegning.py les_fra_kontroll 
Traceback (most recent call last):
  File "/tmp/kjede-woqpqjcf/repo/verktoy/fasade_tegning.py", line 20, in <module>
    import fitz
ModuleNotFoundError: No module named 'fitz'



