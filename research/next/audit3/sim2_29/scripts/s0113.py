from util import *
fr=frames('simulation_0113')
P=[]
for i in sorted(fr):
    f=fr[i].astype(np.int32); B,G,R=f[...,0],f[...,1],f[...,2]
    m=((np.maximum(R,B)-G>60)&(R>110)).astype(np.uint8)
    m[:250,:]=0; m[800:,:]=0; m[:,:250]=0; m[:,800:]=0
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); P.append((i,cen[k][0],cen[k][1],st[k,2],st[k,3]))
P=np.array(P)
t=P[:,0]; 
for c in (1,2):
    print(np.polyfit(t,P[:,c],1))
vx=np.polyfit(t,P[:,1],1)[0]; vy=np.polyfit(t,P[:,2],1)[0]
print('speed px/f',np.hypot(vx,vy),'bbox w,h median',np.median(P[:,3]),np.median(P[:,4]))
print(P[[0,24,60,119]])
