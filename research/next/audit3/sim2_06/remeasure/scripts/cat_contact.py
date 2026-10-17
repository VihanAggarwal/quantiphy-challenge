import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); out=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    dark=(g[780:960,:]<60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(dark); k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]; x0=max(x-40,0); x1=x+w+40
    sub=g[780:960,x0:x1]
    # non-white pixels; exclude chair legs (pinkish): use saturation & value: chair legs have hue reddish; cat white paws are near-gray
    hsv=cv2.cvtColor(f[780:960,x0:x1],cv2.COLOR_BGR2HSV)
    nonwhite=(sub<235)&(hsv[:,:,1]<40)
    nw=nonwhite.astype(np.uint8)
    # keep component(s) touching dark cat blob region dilated
    catreg=cv2.dilate((lab[:,x0:x1]==k).astype(np.uint8),np.ones((25,25),np.uint8))
    m=nw&catreg
    ys,xs=np.nonzero(m)
    out.append((i,ys.max()+780, np.percentile(ys,99.5)+780, xs.min()+x0, xs.max()+x0, cen[k][1]+780, a))
    i+=1
O=np.array(out,float)
print(v,'paw bottom max: median %.1f min %.1f max %.1f'%(np.median(O[:,1]),O[:,1].min(),O[:,1].max()))
t=O[:,0]
print('bottom trend px/frame %.4f'%np.polyfit(t,O[:,1],1)[0],'dark cy trend %.4f'%np.polyfit(t,O[:,5],1)[0],'dark area trend %.2f/frame of mean %.0f'%(np.polyfit(t,O[:,6],1)[0],O[:,6].mean()))
print('per-frame bottom', O[:,1].astype(int).tolist())
