// Lint av den sammensatte modulen (ut/enkel/index.html → modul). Rødt = ikke publisert. Reglene er de som har bitt oss: konstant tilordnet på nytt, udefinerte navn.
export default [{
  files: ['**/*.js'],
  languageOptions: { ecmaVersion: 2023, sourceType: 'module', globals: { window:'readonly', document:'readonly', location:'readonly', navigator:'readonly', performance:'readonly', requestAnimationFrame:'readonly', setTimeout:'readonly', clearTimeout:'readonly', addEventListener:'readonly', innerWidth:'readonly', innerHeight:'readonly', devicePixelRatio:'readonly', sessionStorage:'readonly', URLSearchParams:'readonly', KeyboardEvent:'readonly', Float32Array:'readonly', console:'readonly', fetch:'readonly', screen:'readonly', Image:'readonly', atob:'readonly', Uint8Array:'readonly', Blob:'readonly', URL:'readonly' } },
  rules: { 'no-const-assign':'error', 'no-undef':'error', 'no-redeclare':'error', 'no-dupe-keys':'error', 'no-unreachable':'error', 'no-unused-vars':'off' }
}];
