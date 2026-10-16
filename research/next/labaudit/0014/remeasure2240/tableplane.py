import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
Pt,Pb,e,h,n=np.load('model.npy')
pen=1.6725*ray(468.3,437.2); book=1.665*ray(654,410.7); cookie=1.7355*ray(486,390); cup=1.727*ray(471,368)
# plane through Pb containing h and pen
nt=np.cross(h,pen-Pb); nt/=np.linalg.norm(nt)
if nt@(-Pb)<0: nt=-nt
print('table normal (toward cam)',nt)
for nm,P in [('book',book),('cookie',cookie),('cup',cup),('Pt',Pt)]:
    print(nm,'height above table plane %.1f cm'%(100*nt@(P-Pb)))
ang=np.degrees(np.arccos(abs(e@nt)))
print('slope direction vs table normal: %.1f deg -> incline angle %.1f deg'%(np.degrees(np.arccos(abs(e@nt))),90-ang))
th=np.radians(90-ang)
for k,nm in [(5/7,'solid'),(3/5,'hollow-shell'),(1,'sliding')]:
    print(nm,'a=%.2f m/s2'%(9.81*np.sin(th)*k))
# camera tilt
print('camera optical axis vs table normal %.1f deg'%np.degrees(np.arccos(abs(nt[2]))))
