import cv2,numpy as np
f=711.0; cx,cy=640.,360.
M=cv2.imread('table_mask.png',0)>0
# left boundary: for rows 360..480, first table pixel from left; right boundary for rows 320..440: last pixel
L=[];R=[]
for y in range(355,481):
    xs=np.nonzero(M[y,380:760])[0]
    if len(xs): L.append((380+xs[0],y))
for y in range(318,445):
    xs=np.nonzero(M[y,380:760])[0]
    if len(xs): R.append((380+xs[-1],y))
L=np.array(L,float);R=np.array(R,float)
def fit(P):
    mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu); d=Vt[0]; res=(P-mu)@np.array([-d[1],d[0]]); return mu,d,np.abs(res).max()
mL,dL,rL=fit(L); mR,dR,rR=fit(R)
print('left line',mL,dL,'maxres',rL); print('right line',mR,dR,'maxres',rR)
# vanishing point
l1=np.cross([*mL,1],[*(mL+dL),1]); l2=np.cross([*mR,1],[*(mR+dR),1]); v=np.cross(l1,l2); v=v[:2]/v[2]
print('VP side edges',v)
d2=np.array([(v[0]-cx)/f,(v[1]-cy)/f,1.]); d2/=np.linalg.norm(d2)
if d2[2]<0: d2=-d2
Pt,Pb,e,h,n=np.load('model.npy')
print('h.d2 (should be ~0)',h@d2)
nt=np.cross(h,d2); nt/=np.linalg.norm(nt)
if nt@(-Pb)<0: nt=-nt
print('table normal',nt,'axis vs normal %.1f deg'%np.degrees(np.arccos(abs(nt[2]))))
ang=np.degrees(np.arccos(abs(e@nt))); th=np.radians(90-ang)
print('incline %.1f deg'%(90-ang),'a solid %.2f hollow %.2f'%(9.81*np.sin(th)*5/7,9.81*np.sin(th)*3/5))
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
pen=1.6725*ray(468.3,437.2); book=1.665*ray(654,410.7)
for nm,P in [('pen',pen),('book',book),('Pt',Pt)]: print(nm,'height above plane through Pb: %.1f cm'%(100*nt@(P-Pb)))
np.save('table_normal.npy',nt)
