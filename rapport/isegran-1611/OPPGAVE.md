# Isegran 16.11 – brygga, Isegranhuset, småhusene, Renessansehagen

Bestilt av Fable 16.11 17:45 etter Vegar 17:08. Worktree ~/sot-maskin/voldport, gren gate/voldport-1411 (= /rask). Commit på grenen, publiser til /rask med sh rask.sh når alt under er grønt og sett. /prove og forsiden røres ikke.
Les LESMEG.md først. Regler i kjeden, ikke plaster: alt endres i kilder/ eller verktoy/, aldri i data/ for hånd.

## 1. Gangvei-bånd på brygga (feil, Vegar: «rare greiene på brygga»)
- Funn (Fable): data/veier.json indeks 891 (footway, 5 pkt, -400,120 → -418,93) og 961 (footway -418,93 → -414,85) ligger oppå brygge br-2 (Isegran nord, ved pb-17/pb-18). Tegnes som hevet bånd med sider ned i vannet (mesh x -449..-411, y -1,9..10,7).
- Regel: en vei/gangvei som ligger på en brygge (>= 50 % av lengden inne i et brygge-omriss i data/brygger.json) tegnes ikke; brygga er flaten. Gjelder ALLE brygger. Legg regelen der veier.json bygges (verktoy), og en regel i regler/ som er rød hvis en vei ligger på brygge.
- Bevis: før/etter fra samme kamera ved br-2.

## 2. Isegranhuset bnr-193867464 (Vegar 16.11)
- Veggfarge #c58c59 = (197,140,89). Takfarge: rød takstein NCS S 4050-Y60R ≈ #9E4E2C = (158,78,44) (plan-home: h18 s72 v62). Skyggetoner (veggs/taks) etter samme regel som resten av byen. Kilde i rettelsen: «Vegar 16.11» og «NCS S 4050-Y60R».
- Taket er VALMTAK (Vegars fotos: ovenfra + fasade), ikke saltak med gavl. Sjekk mot ortofoto 2024.
- Fasaden mot vannet (lange siden mot hagen og elva): 2 etasjer x 5 vinduer = 10 vinduer (Vegar), 2 piper (finnes), 4 tykke loddrette lister/pilastre i veggen (Vegar). Vinduene er hvite med sprosser, vegg av stående panel.
- Plassering langs fasaden (Fable målte Vegars foto, rettet for perspektiv med hjørnehøydene 405/280 px; andel fra VENSTRE hjørne sett fra hagen, fasadelengde 19,33 m): vindu 0,195 · 0,580 · 0,808 · 0,856 (par med 0,808) · 0,953; lister 0,481 · 0,661 · 0,741 · 0,906. Samme vindusakser i begge etasjer. Usikkerhet ca. ±0,03. Siste vindu (0,953) ligger tett på hjørnet: kontroller mot ortofoto/skyggen; er det urimelig, flytt mot 0,92 og noter det.
- Erstatt de 7 jevnt fordelte vinduene på denne veggen (data/bygg.json vind) via kilden. Gavlsidene: behold, merk «antatt».

## 3. De to småhusene ved vannet (Vegar: samme farge som hovedhuset)
- Lysthuset bnr-193867456 og det andre lille huset ved hagen/vannkanten (Vegars ovenfra-foto: to små hus, ett i hvert ytre hjørne av hagen mot vannet). Finnes det andre ikke i bygg.json: legg det inn fra ortofoto 2024 som pb-nr med kilde.
- Vegg #c58c59, tak samme som hovedhuset, lite valmtak slik fotoet viser.

## 4. Renessansehagen (Vegar: tegn den fra flyfotoet)
- Ligger mellom Isegranhuset og vannet. Tegn fra ortofoto 2024: rektangulært felt omkranset av grusgang, delt i felt med diagonale gangstier (X), lave buksbomhekker som kanter, bed med grønt innenfor. Lav mur/kaikant mot vannet.
- Utvid data/flater.json (grus, hekk 0,4–0,5 m, bed) via verktoy, kilde «ortofoto 2024 (Renessansehagen)». Ingen trær i hagen.

## Ikke rør
Fortet pb-4, Tårnet, Voldporten-arbeidet, /prove, forsiden.

## Svar (kommentar på saken)
commit-hash(er), /rask-versjon, stier til bilder: før/etter brygga; Isegranhuset rett forfra fra hagen; ovenfra over hagen. Bilder med ekte GPU (PW_GPU=1), LEST før svar. Tak 90 min; går det over: stopp og skriv hva som gjenstår.
