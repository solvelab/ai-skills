# Open ocean

regimes: `dispersive-wave-field`
view: from a stated eye height, horizon in frame; the perspective relations depend on it

| fact | value | source |
|---|---|---|
| dispersion | `c = sqrt(gL/2π)`; L=12 m → 4.33 m/s, 68 m → 10.30, 140 m → 14.78 | deep-water gravity waves |
| group speed | c/2 | deep water |
| fully developed sea | `Hs = 0.21·U²/g`; at U=9 m/s → 1.73 m, peak period 6.57 s, peak wavelength 67.5 m | wave climatology |
| crest shape | Stokes 2nd order, `η = A[cos θ + (Ak/2)cos 2θ]` | wave theory |
| breaking limit | `H/L = 1/7`, `Ak = 0.449`, crest angle 120° | Michell |
| surface slope | `s² = 0.003 + 0.00512·U`; U=9 → 0.0491, rms slope 12.7° | Cox & Munk, from sun-glitter photographs |
| whitecap coverage | `W = 3.84e-6·U^3.41`; 0.69% at 9 m/s | Monahan & O'Muircheartaigh |
| sun angular diameter | 0.53°, so the specular tolerance on facet tilt is 0.0046 rad | astronomy |

The number that decides the design: four drawn wave trains carry `s² = 0.0054`, **11% of the real
slope variance**. The other 89% is in waves centimetres long that no scene will draw, so glitter is
a probability with `σ = 0.209`, not a test on the drawn surface.
