import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0037x.mp4')
i=0
while True:
    ok,f=c.read()
    if not ok: break
    F=f.astype(float); lum=F.max(2)
    # ping pong ball: white blob not on table (y<450) and small
    m=(lum>120).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cands=[(k,st[k]) for k in range(1,n) if 150<st[k,4]<3000 and st[k,1]<455]
    for k,s in cands:
        a=np.clip(lum/200,0,1)*(lab==k)
        area=a.sum()
        print(i,'blob',s.tolist(),'cen',cen[k].round(1).tolist(),'alpha-area eqdiam %.2f'%(2*np.sqrt(area/np.pi)), 'bin-area eqdiam %.2f'%(2*np.sqrt(s[4]/np.pi)))
    i+=1
