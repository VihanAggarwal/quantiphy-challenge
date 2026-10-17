from util import *
fr=frames('simulation_0220')
n=len(fr)
bg=np.median(np.stack([fr[i] for i in range(n)]),axis=0).astype(np.float32)
R=[]
for i in range(n):
    d=np.abs(fr[i].astype(np.float32)-bg).max(axis=2)
    m=(d>20).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m[:500]=0
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); cx=cen[k][0]
    sel=[q for q in range(1,nl) if abs(cen[q][0]-cx)<150 and st[q,4]>80]
    mm=np.isin(lab,sel); yy,xx=np.nonzero(mm)
    R.append((i,xx.min(),xx.max(),yy.min(),yy.max(),xx.mean(),yy.mean()))
R=np.array(R,float)
for r in R[::6]: print(np.round(r,1))
print('x-centroid slope px/f',np.polyfit(R[:,0],R[:,5],1)[0], 'px/s', 24*np.polyfit(R[:,0],R[:,5],1)[0])
print('bbox-centre slope', 24*np.polyfit(R[:,0],(R[:,1]+R[:,2])/2,1)[0])
print('heights',(R[:,4]-R[:,3])[::3])
