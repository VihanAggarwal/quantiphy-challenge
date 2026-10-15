# internet_0046 — cup pulled by rope across a table (static camera)
- Camera static (rail endpoints identical in frames 0 and 48). The cup is visible in frames 21-43 and moves to the right while speeding up.
- Scale: the cup height at t=1.1 is ~570 px (rim y~299, lowest front base y~869, from a 2x crop). 10.5 cm / 570 px = 1.842e-4 m/px.
- Track: the dark body is found by background difference in rows 320-480, and its centre is the midpoint of the left and right edges (this cancels motion blur). Centres for frames 27-39 are 274.5 ... 1606 px.
- Fits: a quadratic or cubic fit gives v(1.0)=0.545, v(1.1)=0.615-0.621, v(1.2)=0.685 m/s and a~0.70 m/s^2. Backward differences agree: 0.525, 0.63, 0.685.
- Displacements: 1.0-1.1 s = 5.84 cm; 1.1-1.3 s = 13.65 cm. The raw and fitted values agree.
- Confidence: medium-high. The main uncertainty is the pixel height of the cup (~3%), plus slight perspective as the cup moves closer.
