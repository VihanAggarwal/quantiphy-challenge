import cv2, numpy as np, json
fr='/home/user/quantiphy-challenge/research/next/labaudit/0031/frames/'
out={}
for r in ['0','s','x']:
    T=[];W=[]
    for i in range(49):
        f=cv2.imread(fr+f'r{r}_{i:02d}.png')
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        # tennis: yellow
        m=cv2.inRange(hsv,(22,90,90),(45,255,255))
        m[:300]=0
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n>1:
            k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
            T.append([i,float(cen[k][0]),float(cen[k][1]),int(w),int(h),int(a),float(2*np.sqrt(a/np.pi))])
        else: T.append([i,None])
        # white ball: high V low S, in table region
        m2=cv2.inRange(hsv,(0,0,170),(180,70,255))
        m2[:380]=0; m2[520:]=0
        m2=cv2.morphologyEx(m2,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m2)
        best=None
        for k in range(1,n):
            x,y,w,h,a=st[k]
            if a<60 or a>3000: continue
            if w>2.2*h or h>2.2*w: continue
            fill=a/(w*h)
            if fill<0.5: continue
            if best is None or a>st[best][4]: best=k
        if best is not None:
            x,y,w,h,a=st[best]
            W.append([i,float(cen[best][0]),float(cen[best][1]),int(w),int(h),int(a),float(2*np.sqrt(a/np.pi))])
        else: W.append([i,None])
    out[r]=dict(T=T,W=W)
    print('render',r)
    for t,w in zip(T,W):
        print(t[0], ['%.1f'%v if isinstance(v,float) else v for v in t[1:]], ['%.1f'%v if isinstance(v,float) else v for v in w[1:]])
json.dump(out,open(fr+'../track.json','w'))
