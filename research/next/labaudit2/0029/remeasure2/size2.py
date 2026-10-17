import cv2,numpy as np,json
T=json.load(open('track_raw.json'))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0029x.mp4'); frames=[]
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(f)
def fit_circle(p):
    A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; b=(p**2).sum(1)
    s=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(s[2]+s[0]**2+s[1]**2); return np.array([s[0],s[1],r])
def edges(V,x0,y0,angs):
    P=[]
    for a in angs:
        ang=np.radians(a); d=np.array([np.cos(ang),-np.sin(ang)])
        rs=np.arange(8,40,0.2); xs=(x0+rs*d[0]).astype(np.float32); ys=(y0+rs*d[1]).astype(np.float32)
        v=cv2.remap(V,xs[None],ys[None],cv2.INTER_LINEAR)[0]
        # 50% crossing relative to local interior (max over r-window before) and outside (0 for black)
        g=-np.gradient(v); k=int(np.argmax(g))
        ref=np.median(v[max(0,k-40):max(1,k-12)])
        # find crossing of ref/2 near k
        idx=np.where((v[:-1]>=ref/2)&(v[1:]<ref/2))[0]
        if len(idx)==0 or k<5: continue
        j=idx[np.argmin(np.abs(idx-k))]; fr=(v[j]-ref/2)/(v[j]-v[j+1]); r=rs[j]+fr*0.2
        P.append((a,x0+r*d[0],y0+r*d[1],r))
    return np.array(P)
res={}
for i in range(22,49):
    V=cv2.cvtColor(frames[i],cv2.COLOR_BGR2HSV)[:,:,2].astype(np.float32)
    V=cv2.GaussianBlur(V,(3,3),0)
    x0,y0=T['x'][i][1],T['x'][i][2]
    # iterate centre
    for it in range(3):
        Pu=edges(V,x0,y0,np.arange(15,166,5))
        cu=fit_circle(Pu[:,1:3])
        if cu[2]>35 or len(Pu)<10: print('bad',i,cu); break
        x0,y0=cu[0],cu[1]
    Pa=edges(V,x0,y0,np.arange(0,360,5))
    ca=fit_circle(Pa[:,1:3])
    # residual-trimmed
    rr=np.hypot(Pa[:,1]-ca[0],Pa[:,2]-ca[1])-ca[2]; keep=np.abs(rr)<2.5*np.median(np.abs(rr))+0.5
    ca2=fit_circle(Pa[keep,1:3])
    # horizontal and vertical extents through centre
    res[i]=dict(up=cu.tolist(),all=ca2.tolist())
    print(f'v{i:02d} upper: c=({cu[0]:6.1f},{cu[1]:6.1f}) D={2*cu[2]:5.2f} | all(trim {keep.sum()}/{len(keep)}): c=({ca2[0]:6.1f},{ca2[1]:6.1f}) D={2*ca2[2]:5.2f}')
json.dump(res,open('size_x2.json','w'))
