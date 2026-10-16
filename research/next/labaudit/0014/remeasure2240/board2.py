import numpy as np
c=np.load('board_contour.npy')
corn=np.array([[501,313],[593,304],[609,407],[510,422]],float) # TL TR BR BL
lines=[]
for a,bb in [(0,1),(1,2),(2,3),(3,0)]:
    A,B=corn[a],corn[bb]; d=B-A; L=np.linalg.norm(d); d/=L; nrm=np.array([-d[1],d[0]])
    s=(c-A)@d; o=(c-A)@nrm
    sel=(s>0.15*L)&(s<0.85*L)&(np.abs(o)<6)
    P=c[sel]; mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu); dirn=Vt[0]
    lines.append((mu,dirn)); 
def inter(l1,l2):
    (p,d),(q,e)=l1,l2
    A=np.array([d,-e]).T; t=np.linalg.solve(A,q-p); return p+t[0]*d
names=['TL','TR','BR','BL']
pts={}
pts['TL']=inter(lines[3],lines[0]); pts['TR']=inter(lines[0],lines[1]); pts['BR']=inter(lines[1],lines[2]); pts['BL']=inter(lines[2],lines[3])
for k,v in pts.items(): print(k,np.round(v,1))
np.save('board_corners.npy',np.array([pts[k] for k in names]))
print('top mid',(pts['TL']+pts['TR'])/2,'bot mid',(pts['BL']+pts['BR'])/2)
