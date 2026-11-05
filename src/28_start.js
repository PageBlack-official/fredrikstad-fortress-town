import { TILSTAND } from './tilstand.js';
// ---- lasting: omrisset av festningen tegnes mens kartet laster (kropp.html #laster), og tones ut når byen er tegnet første gang ----
const laster = document.getElementById('laster');
if (laster) { const se = () => { if (TILSTAND._synlig) { laster.classList.add('ferdig'); setTimeout(() => laster.remove(), 800); } else requestAnimationFrame(se); }; requestAnimationFrame(se); }
