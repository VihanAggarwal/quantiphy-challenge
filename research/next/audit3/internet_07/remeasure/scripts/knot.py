from load import load
import numpy as np, cv2, json
fr=load(gray=False)
D=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/linefit.json'))
Rb=dict(zip(D['fr'],D['R']))
S=[]
for f in fr:
    g=cv2.GaussianBlur(f.astype(np.float32),(0,0),1.0)
    S.append(g[:,:,2]-g[:,:,0])
# locate knot: in rows 540-630, columns Rb+60..Rb+260, find the leftmost column where S>25 in >=4 rows
res={}
for i in range(55,80):
    a=int(Rb[i]+60); b=int(min(1919,Rb[i]+300))
    if b-a<30: continue
    blk=S[i][520:640,a:b]
    colcnt=(blk>22).sum(0)
    xs=np.where(colcnt>=4)[0]
    if len(xs)==0: continue
    res[i]=a+xs[0]
print({k:int(v) for k,v in res.items()})
def sub(r):
    _,mv,_,ml=cv2.minMaxLoc(r); X,Y=ml; dx=dy=0
    if 0<X<r.shape[1]-1:
        p,q,s=r[Y,X-1],r[Y,X],r[Y,X+1]; dx=0.5*(p-s)/(p-2*q+s)
    if 0<Y<r.shape[0]-1:
        p,q,s=r[Y-1,X],r[Y,X],r[Y+1,X]; dy=0.5*(p-s)/(p-2*q+s)
    return X+dx,Y+dy,mv
# frame-to-frame match of S map around knot: template rows 530-630, cols knot-25..knot+55
tr={}
ks=sorted(res)
for i in ks:
    if i+1 not in res: continue
    x0=int(res[i])-25; x1=x0+80
    T=S[i][530:630,x0:x1]
    exp=res[i+1]-res[i]
    sx0=int(x0+exp)-25; Sw=S[i+1][515:645,sx0:sx0+80+50]
    r=cv2.matchTemplate(Sw,T,cv2.TM_CCOEFF_NORMED)
    X,Y,mv=sub(r)
    tr[i]=(sx0+X-x0, Y-15, mv)
for i in sorted(tr): print(i,'knotL %d'%res[i],'disp %.2f dy %.2f corr %.3f'%tr[i])
json.dump({'knot':{str(k):float(v) for k,v in res.items()},'disp':{str(k):list(map(float,v)) for k,v in tr.items()}},open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/knot.json','w'))
