import cv2,numpy as np,sys,json
res={}
for tag in ['','s','x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0029{tag}.mp4')
    out=[];i=0
    while True:
        ok,f=c.read()
        if not ok: break
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        m=cv2.inRange(hsv,(22,70,90),(45,255,255))
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n>1:
            j=1+np.argmax(st[1:,4])
            x,y,w,h,a=st[j]
            ys,xs=np.nonzero(lab==j)
            out.append([i,float(xs.mean()),float(ys.mean()),int(w),int(h),int(a), x,y])
        else: out.append([i,None])
        i+=1
    res[tag]=out
json.dump(res,open('track_raw.json','w'),default=int)
for k in range(len(res[''])):
    print(k, *[ ' '.join(f'{v:7.1f}' if isinstance(v,float) else f'{v}' for v in res[t][k][1:6]) + ' |' for t in ['','s','x']])
