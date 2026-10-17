from util import *
fr=frames('internet_0025_segmented')
n=len(fr)
R=[]
for i in range(0,n):
    f=fr[i].astype(np.int32)
    m=(f.min(axis=2)<200).astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    sel=[q for q in range(1,nl) if st[q,4]>20]
    mm=np.isin(lab,sel); yy,xx=np.nonzero(mm)
    R.append((i,xx.min(),xx.max(),yy.min(),yy.max(),xx.mean(),yy.mean()))
R=np.array(R,float)
for r in R[::30]: print(np.round(r,1))
print('last',R[-1])
t=R[:,0]/29.97
for c,nm in ((1,'xmin'),(2,'xmax'),(5,'xmean')):
    print(nm,'slope px/s',np.polyfit(t,R[:,c],1)[0])
print('len px median',np.median(R[:,2]-R[:,1]))
