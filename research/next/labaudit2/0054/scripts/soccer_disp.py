from common import *
R=0.10
print('camera b (size ranges anchored at stated 3.254 m at 2.0 s)')
for s48 in [42.4,43.0,44.0]:
    K=(3.254+R)*s48
    for s25,s35,lab in [(63,55.8,'minor'),(62,58.1,'deq'),(64,57,'mid')]:
        for c25 in [(921,606.5),(919.1,605.9)]:
            P25=(K/s25-R)*ray(*c25); P35=(K/s35-R)*ray(884.8,488.9)
            print(f'  s48={s48} {lab} c25={c25}: r25={K/s25-R:.3f} r35={K/s35-R:.3f} disp={np.linalg.norm(P35-P25):.3f}  lateral-only={np.linalg.norm(ray(884.8,488.9)-ray(*c25))*(K/s25+K/s35)/2:.3f}')
print('camera a (size ranges, diameter D)')
for D in [0.195,0.20,0.205,0.21]:
    for s25,s35 in [(59,72),(61,74),(62,70)]:
        r25=F*D/s25; r35=F*D/s35
        P25=(r25-D/2)*ray(151.3,606.0); P35=(r35-D/2)*ray(66.4,681.5)
        print(f'  D={D} s25={s25} s35={s35}: r25c={r25:.3f} r35c={r35:.3f} disp={np.linalg.norm(P35-P25):.3f}')
