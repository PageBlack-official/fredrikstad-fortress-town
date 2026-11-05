// Tilstanden tegneløkka deler med lyset, speilet og interaksjonen. Én eier: dette objektet. Andre moduler leser og skriver
// TILSTAND.<navn>, så det står i koden hvor en verdi endres (før var de løse variabler i én fil og ble skrevet fra tre andre).
export const TILSTAND = {
  skyggeSkitten: true,   // skyggekartet må tegnes på nytt (sola, husene eller introen har endret seg)
  introDone: false,      // introen er ferdig
  _synlig: false,        // byen er tegnet minst én gang
  speilInn: 0,           // speilet toner inn etter introen
  speilFrisk: false,     // speilet er tegnet etter siste bevegelse
  sistBeveg: 0,          // tidspunkt (ms) da kartet sist beveget seg
  sistTegnet: 0,         // tidspunkt (ms) da byen sist ble tegnet
  fullTegnet: false,     // bildet er tegnet ferdig i ro
};

// Det en tidlig modul trenger fra en senere (tegneløkka, husvalget, ferga), slås opp i SENERE når det brukes, ikke når modulen lastes.
// Da lastes modulene i rekkefølgen i main.js, uten sirkler. Eieren registrerer navnene nederst i sin fil.
export const SENERE = {};
export function registrer(navn){ for(const [k, f] of Object.entries(navn)) Object.defineProperty(SENERE, k, { get: f, enumerable: true }); }
