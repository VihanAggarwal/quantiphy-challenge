import cv2,numpy as np
for v in ['captured_0053','captured_0053s','captured_0053x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    acc=[]
    while True:
        ok,f=c.read()
        if not ok: break
        acc.append(f[395:455,535:600].astype(float))
    m=np.median(np.array(acc),0)
    if v=='captured_0053x': p2=255-np.clip(m[...,1]-np.maximum(m[...,0],m[...,2]),0,255)
    else: p2=m.min(2)
    rows=[];mids=[]
    for y in range(12,48):
        p=p2[y]; d=np.diff(p)
        li=np.argmax(d[8:28])+8; ri=np.argmax(-d[30:50])+30
        def sp(arr,i):
            a,b,cc=arr[i-1],arr[i],arr[i+1]; den=a-2*b+cc
            return i+(0.5*(a-cc)/den if den!=0 else 0)
        L=sp(d,li)+0.5+535; R=sp(-d,ri)+0.5+535
        rows.append(395+y); mids.append((L+R)/2)
        print(v,395+y,round(L,2),round(R,2),round(R-L,2),round((L+R)/2,2))
    rows=np.array(rows); mids=np.array(mids)
    sel=(rows>=413)&(rows<=440)
    k=np.polyfit(rows[sel],mids[sel],1)
    print(v,'midline slope dx/dy',k[0],'tilt deg',np.degrees(np.arctan(k[0])))
