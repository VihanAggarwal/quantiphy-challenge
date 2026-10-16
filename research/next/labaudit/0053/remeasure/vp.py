import numpy as np
S=np.load('stripes.npy')
# lines: n.(p) = c, n = normal of direction (1,s)
A=[];b=[]
for x0,y0,s,coh in S:
    d=np.array([1,s]); d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])
    A.append(n); b.append(n@np.array([x0,y0]))
A=np.array(A); b=np.array(b)
vp2=np.linalg.lstsq(A,b,rcond=None)[0]
res=A@vp2-b
print('VP2 (stripes)',vp2.round(1),'residual px rms %.1f'%np.sqrt(np.mean(res**2)))
# VP1: left wall base x=130-0.0295(y-250), right wall line through (760,133),(1260,496)
# left line points
L1=np.array([130.0,250.0]); L2=np.array([117.0,690.0])
R1=np.array([760.0,133.0]); R2=np.array([1260.0,496.0])
def inter(p1,p2,q1,q2):
    a=np.cross(np.append(p1,1),np.append(p2,1)); c=np.cross(np.append(q1,1),np.append(q2,1)); v=np.cross(a,c); return v[:2]/v[2]
vp1=inter(L1,L2,R1,R2); print('VP1 (walls)',vp1.round(1))
f=711.0; c=np.array([640.,360.])
print('orthogonality check: (v1-c).(v2-c) = %.0f, -f^2 = %.0f, implied f = %.0f'%((vp1-c)@(vp2-c),-f*f,np.sqrt(max(-(vp1-c)@(vp2-c),0))))
# horizon line through vp1, vp2 -> normal vector of floor in camera coords: n ~ K^T l
l=np.cross(np.append(vp1,1),np.append(vp2,1))
K=np.array([[f,0,c[0]],[0,f,c[1]],[0,0,1]])
n=K.T@l; n/=np.linalg.norm(n)
if n[1]>0: n=-n   # up vector should have negative y (image y down)
print('up normal in cam coords',n.round(4))
pitch=np.degrees(np.arcsin(-n[2])); roll=np.degrees(np.arctan2(n[0],-n[1]))
print('pitch %.1f deg, roll %.2f deg'%(pitch,roll))
np.save('up_vp.npy',n)
# alternative: VP1 from right wall + vp2 only? Also horizon from stripes VP2 + VP1
