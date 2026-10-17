from common import *
print('camera a: orange stated 1.81 at (585.6,678.6); soccer range variants')
Po=1.81*ray(585.6,678.6)
for rs in [2.15,2.20,2.25,2.30,2.35,2.40]:
    for cs in [(151.3,606.0),(156.3,603.0)]:
        Ps=rs*ray(*cs); print('  soccer surf range %.2f at %s: dist=%.3f'%(rs,cs,np.linalg.norm(Po-Ps)))
print('camera a physical (centres): orange centre range 1.81+0.116, soccer centre')
for rs in [2.29,2.35,2.45]:
    print('  ',rs, '%.3f'%np.linalg.norm(1.926*ray(585.6,678.6)-rs*ray(151.3,606.0)))
print('camera b: orange at (537.9,385.8) range variants; soccer at (921,606.5)')
for ro in [1.81,2.6,2.7,2.8]:
    for rs in [2.10,2.16,2.22,2.28]:
        print('  orange %.2f soccer %.2f: dist=%.3f'%(ro,rs,np.linalg.norm(ro*ray(537.9,385.8)-rs*ray(921,606.5))))
