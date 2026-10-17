import cv2, numpy as np, sys, json
vid = sys.argv[1] if len(sys.argv)>1 else ''
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0031%s.mp4'%vid)
F=[]
while True:
    ok,x=c.read()
    if not ok: break
    F.append(x)

def fit_circle(pts):
    x=pts[:,0].astype(float); y=pts[:,1].astype(float)
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
    s=np.linalg.lstsq(A,b,rcond=None)[0]
    cx,cy=s[0],s[1]; r=np.sqrt(s[2]+cx*cx+cy*cy)
    return cx,cy,r

out=[]
for i,fr in enumerate(F):
    hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV)
    # tennis: yellow, high saturation
    m=((hsv[...,0]>=20)&(hsv[...,0]<=40)&(hsv[...,1]>120)&(hsv[...,2]>90)).astype(np.uint8)
    m[:350]=0; m[600:]=0; m[:, :550]=0; m[:, 900:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    rec={'i':i}
    if n>1:
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        cnts,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cnt=max(cnts,key=len)[:,0,:]
        cx,cy,r=fit_circle(cnt)
        rec.update(t_bbox=[int(x),int(y),int(w),int(h)],t_area=int(a),t_c=[float(cx),float(cy)],t_r=float(r),t_req=float(np.sqrt(a/np.pi)), t_mom=[float(cen[k][0]),float(cen[k][1])])
    # white ball: low sat, bright
    m2=((hsv[...,1]<70)&(hsv[...,2]>175)).astype(np.uint8)
    m2[:380]=0; m2[520:]=0; m2[:, :560]=0; m2[:, 720:]=0
    m2=cv2.morphologyEx(m2,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m2)
    if n>1:
        k=1+np.argmax(st[1:,4])
        x,y,w,h,a=st[k]
        cnts,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cnt=max(cnts,key=len)[:,0,:]
        cx,cy,r=fit_circle(cnt)
        rec.update(w_bbox=[int(x),int(y),int(w),int(h)],w_area=int(a),w_c=[float(cx),float(cy)],w_r=float(r),w_req=float(np.sqrt(a/np.pi)),w_mom=[float(cen[k][0]),float(cen[k][1])])
    out.append(rec)
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/track%s.json'%(vid or 'a'),'w'))
for r in out:
    print(r['i'], r.get('t_bbox'), '%.1f %.1f r=%.1f req=%.1f'%(*r['t_c'],r['t_r'],r['t_req']) if 't_c' in r else '', '|', r.get('w_bbox'), '%.1f %.1f r=%.1f req=%.1f'%(*r['w_c'],r['w_r'],r['w_req']) if 'w_c' in r else '')
