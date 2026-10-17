import cv2,numpy as np
for v in ['captured_0053','captured_0053s','captured_0053x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    acc=[]
    while True:
        ok,f=c.read()
        if not ok: break
        acc.append(f[395:455,535:600].astype(float))
    m=np.median(np.array(acc),0)
    g=m.mean(2) if v!='captured_0053x' else None
    if v=='captured_0053x':
        g=255-np.clip(m[...,1]-np.maximum(m[...,0],m[...,2]),0,255)
    if v=='captured_0053s':
        # distance from local background colour
        bgL=m[:, :8].reshape(-1,3).mean(0); bgR=m[:,-8:].reshape(-1,3).mean(0)
        g=None
    out=[]
    for y in range(8,26):
        if v=='captured_0053s':
            row=m[y]; xs=np.arange(row.shape[0])
            # white-ness: min channel
            p=row.min(1)
        else:
            p=g[y]
        # left edge: max positive gradient in x<565-535, right edge: max negative grad in x>30
        d=np.diff(p)
        li=np.argmax(d[10:25])+10; ri=np.argmax(-d[32:50])+32
        # subpixel parabola
        def sp(arr,i):
            a,b,cc=arr[i-1],arr[i],arr[i+1]; den=a-2*b+cc
            return i+(0.5*(a-cc)/den if den!=0 else 0)
        L=sp(d,li)+0.5+535; R=sp(-d,ri)+0.5+535
        out.append((395+y,L,R,R-L))
    print(v)
    for o in out: print('  row %d L %.2f R %.2f W %.2f'%o)
