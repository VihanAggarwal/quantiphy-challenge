import numpy as np
F=711.;CX=640;CY=360
def floorpt(u,v,h,phi,hz=0.0,f=F):
    p=np.radians(phi)
    d=np.array([(u-CX)/f,(v-CY)/f,1.0])
    down=np.array([0,np.cos(p),np.sin(p)])   # world down in camera coords
    t=(h-hz)/(d@down); return t*d
def unit(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
toes=[(251,684),(250.5,681),(253,683)]
heels=[(318.5,651),(317,654),(316,648)]
for h in (0.93,0.96,0.99):
  for phi in (0,1,2):
    L=[np.linalg.norm(floorpt(*t,h,phi,0.01)-floorpt(*hh,h,phi,0.015)) for t in toes for hh in heels]
    c=floorpt(285,656,h,phi,0.04); 
    print('h=%.2f pitch=%d shoe length %.1f-%.1f cm; shoe-centre range (geom) %.3f'%(h,phi,100*min(L),100*max(L),np.linalg.norm(c)))
# label emulation: both clicks with ranges scaled by stated/geom ratio (multiplicative ToF bias) or additive
h,phi=0.96,1
T=floorpt(251,684,h,phi,0.01); H=floorpt(318.5,651,h,phi,0.015); C=floorpt(285,656,h,phi,0.04)
k=2.231/np.linalg.norm(C)
print('geom ranges toe %.3f heel %.3f centre %.3f; k=%.3f'%(np.linalg.norm(T),np.linalg.norm(H),np.linalg.norm(C),k))
print('true len %.1f; mult-bias label %.1f; additive-bias label %.1f; both at 2.231 %.1f'%(
  100*np.linalg.norm(T-H),100*k*np.linalg.norm(T-H),
  100*np.linalg.norm((np.linalg.norm(T)+2.231-np.linalg.norm(C))*unit(251,684)-(np.linalg.norm(H)+2.231-np.linalg.norm(C))*unit(318.5,651)),
  100*np.linalg.norm(2.231*unit(251,684)-2.231*unit(318.5,651))))
