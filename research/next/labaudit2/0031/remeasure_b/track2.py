import cv2, numpy as np, json, sys
vid = sys.argv[1] if len(sys.argv)>1 else ''
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0031%s.mp4'%vid)
F=[]
while True:
    ok,x=c.read()
    if not ok: break
    F.append(x)
def fit_circle(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
    s=np.linalg.lstsq(A,b,rcond=None)[0]
    cx,cy=s[0],s[1]; return cx,cy,np.sqrt(s[2]+cx*cx+cy*cy)
def ball(mask, upper=True):
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(mask)
    if n<2: return None
    k=1+np.argmax(st[1:,4])
    cnts,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnt=max(cnts,key=len)[:,0,:].astype(float)
    cx,cy,r=fit_circle(cnt[:,0],cnt[:,1])
    # refit with upper ~2/3 (exclude bottom contact/shadow region)
    sel=cnt[:,1]<cy+0.3*r
    cx2,cy2,r2=fit_circle(cnt[sel,0],cnt[sel,1])
    x,y,w,h,a=st[k]
    # contour pixels are inner boundary pixel centres -> add 0.5 px for edge
    return dict(c=[cx2,cy2],r=r2+0.5,rall=r+0.5,w=int(w),h=int(h),area=int(a))
out=[]
for i,fr in enumerate(F):
    hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]>=18)&(hsv[...,0]<=42)&(hsv[...,1]>110)&(hsv[...,2]>80)).astype(np.uint8)
    m[:380]=0; m[620:]=0; m[:, :600]=0; m[:, 880:]=0
    t=ball(m)
    m2=((hsv[...,1]<80)&(hsv[...,2]>165)).astype(np.uint8)
    m2[:395]=0; m2[500:]=0; m2[:, :600]=0; m2[:, 710:]=0
    w=ball(m2)
    out.append(dict(i=i,t=t,w=w))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/trk2_%s.json'%(vid or 'a'),'w'))
for o in out:
    s='%2d'%o['i']
    for k in 't','w':
        b=o[k]
        s+= '  %s c=(%.1f,%.1f) r=%.2f rall=%.2f wh=%dx%d'%(k,*b['c'],b['r'],b['rall'],b['w'],b['h']) if b else '  -'
    print(s)
