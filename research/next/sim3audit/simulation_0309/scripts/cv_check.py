import numpy as np
P=np.load('head0302.npy'); d=np.load('joint0302.npz'); vp=d['vp']
P=P[P[:,3]>300]
fr=P[:,0]; t=fr/24.; X=P[:,1:3]
D=X-vp; r=np.linalg.norm(D,axis=1); ang=np.degrees(np.arctan2(D[:,1],D[:,0]))
gl=fr>=51
A=np.polyfit(t[gl],1/r[gl],1); s=-A[1]/A[0]
print('glide-only head patch t*',s)
pred=1/np.polyval(A,t)
for k in range(0,len(fr),3):
    print('%d r=%.1f pred=%.1f dev=%.2f%% ang=%.2f'%(fr[k],r[k],pred[k],100*(r[k]/pred[k]-1),ang[k]))
Aall=np.polyfit(t,1/r,1); print('all-frames t*',-Aall[1]/Aall[0])
