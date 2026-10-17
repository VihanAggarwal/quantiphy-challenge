from util import *
fr=frames('simulation_0131')
bgc=np.array([197,168,139],np.float32)
R=[]
for i in sorted(fr):
    d=np.abs(fr[i].astype(np.float32)-bgc).max(axis=2)
    m=(d>40).astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    R.append((i,x,x+w,y,y+h,w,h,cen[k][1]))
R=np.array(R,float)
for r in R[::12]: print(r)
t=R[:,0]
print('top slope',np.polyfit(t,R[:,3],1)[0],'bottom slope',np.polyfit(t[R[:,4]<1079],R[R[:,4]<1079,4],1)[0])
