import sys; sys.path.insert(0,'scripts')
from load import frames
import numpy as np, cv2
F=frames('simulation_0248',n=49)
np.set_printoptions(suppress=True,precision=2,linewidth=160)
# objects are saturated or dark vs neutral gray bg; use saturation + darkness relative to temporal median
bg=np.median(F,axis=0).astype(np.int16)
recs={'brown':[], 'white':[], 'rabbit':[]}
for k in range(49):
    f=F[k].astype(np.int16)
    hsv=cv2.cvtColor(F[k],cv2.COLOR_BGR2HSV).astype(int)
    D=np.abs(f-bg).sum(axis=2)
    m=((hsv[...,1]>45)|((D>60)&(f.sum(axis=2)<bg.sum(axis=2)-90))).astype(np.uint8)
    m[:400]=0; m[700:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[i],cen[i]) for i in range(1,n) if st[i][4]>150]
    for s,c in comps:
        x,y,w,h,a=s
        # classify by mean colour
        M=lab[y:y+h,x:x+w]
        if a>4000:
            col=F[k][y:y+h,x:x+w][M==np.argmax([0])] if False else None
        recs_k=(k,x,y,w,h,a,c[0],c[1])
        if a<2500: recs['rabbit'].append(recs_k)
        else:
            # brown is the leftmost big
            recs.setdefault('big',[]).append(recs_k)
big=np.array(recs['big']); rab=np.array(recs['rabbit'])
print('big count',len(big),'rabbit count',len(rab))
# split big by frame: leftmost = brown
B=[];W=[]
for k in range(49):
    r=big[big[:,0]==k]
    r=r[np.argsort(r[:,1])]
    if len(r)>=2: B.append(r[0]); W.append(r[-1])
B=np.array(B);W=np.array(W)
for nm,A in [('brown',B),('white',W),('rabbit',rab)]:
    kk=A[:,0]
    p=np.polyfit(kk,A[:,6],1)
    print(nm,'n',len(A),'cx slope %.3f'%p[0],'xmin slope %.3f'%np.polyfit(kk,A[:,1],1)[0],'xmax slope %.3f'%np.polyfit(kk,A[:,1]+A[:,3],1)[0],
          '| w med',np.median(A[:,3]),'p90',np.percentile(A[:,3],90),'h med',np.median(A[:,4]),'| bottom row med',np.median(A[:,2]+A[:,4]-1),'p90',np.percentile(A[:,2]+A[:,4]-1,90),'max',np.max(A[:,2]+A[:,4]-1),'top med',np.median(A[:,2]))
np.save('/dev/null',B) if False else None
