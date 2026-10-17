# Label-style forward differences: clicked centres back-projected at surface range.
import numpy as np
f=711.; pp=np.array([640.,360.])
def ray(p): v=np.array([p[0]-pp[0],p[1]-pp[1],f]); return v/np.linalg.norm(v)
c36=(812.2,77.2); c37v=(844.7,70.3); c35=(735.2,121.1)
print('Convention A: c38->c39 = video36->37, r38=1.402 (stated)')
for r39 in [1.42,1.44,1.46,1.48,1.50,1.52]:
    Q1=1.402*ray(c36); Q2=r39*ray(c37v); print('  r39=%.2f  v=%.2f m/s'%(r39,25*np.linalg.norm(Q2-Q1)))
# lateral only
print('  lateral-only (r39=1.402): %.2f'%(25*np.linalg.norm(1.402*ray(c37v)-1.402*ray(c36))))
print('Convention B: c37->c38, r37=1.402 at the (unseen) c37 click, r38 at video 36')
# c37 image position: ballistic fit midpoint estimate
for c37 in [(775.,96.),(772.,99.),(778.,94.)]:
    for r38 in [1.44,1.46,1.48,1.50]:
        Q1=1.402*ray(c37); Q2=r38*ray(c36); print('  c37=%s r38=%.2f v=%.2f'%(c37,r38,25*np.linalg.norm(Q2-Q1)))
