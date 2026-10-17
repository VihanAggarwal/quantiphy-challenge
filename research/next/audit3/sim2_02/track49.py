import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0249.mp4'); F=[]
while True:
    ok,im=c.read()
    if not ok: break
    F.append(im)
def sat_mask(im):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    return ((hsv[...,1]>60)&(hsv[...,2]>25)).astype(np.uint8) | (hsv[...,2]<60).astype(np.uint8)
res={}
for name,(ya,yb) in {'brown':(280,410),'white':(430,600),'rabbit':(590,632)}.items():
    xs=[]
    for i in range(49):
        m=sat_mask(F[i])[ya:yb]
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4])
        xs.append((st[k,0],st[k,0]+st[k,2]-1,cen[k,0],cen[k,1]+ya,st[k,4],st[k,1]+ya,st[k,1]+st[k,3]+ya-1))
    xs=np.array(xs,float); res[name]=xs
    t=np.arange(49)
    for j,lab_ in [(0,'left'),(1,'right'),(2,'cx')]:
        p=np.polyfit(t,xs[:,j],1); print(name,lab_,'slope %.3f'%p[0])
    print(name,'width med %.1f'%np.median(xs[:,1]-xs[:,0]+1),'cy %.1f'%np.median(xs[:,3]),'yext',np.median(xs[:,5]),np.median(xs[:,6]))
    print('   widths',(xs[::6,1]-xs[::6,0]+1).astype(int))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/t49.npy',np.array([res['brown'],res['white'],res['rabbit']]))
