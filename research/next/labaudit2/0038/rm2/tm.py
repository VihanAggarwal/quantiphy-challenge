import cv2, numpy as np, json, sys
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
v=sys.argv[1] if len(sys.argv)>1 else 'x'
ref=int(sys.argv[2]) if len(sys.argv)>2 else 24
tr=json.load(open(D+'track_x.json'))
G=[cv2.GaussianBlur(cv2.cvtColor(cv2.imread(D+'f%s/%02d.jpg'%(v,i)),cv2.COLOR_BGR2GRAY),(3,3),0).astype(np.float32) for i in range(49)]
# reference center in ref frame: use blob bbox from bg-sub (x range) & vertical extent from brightness profile
cx0,cy0=tr[ref]['cx'],tr[ref]['cy']
hw,hh=30,26
T=G[ref][int(cy0)-hh+4:int(cy0)+hh+4, int(cx0)-hw:int(cx0)+hw]
tc=np.array([int(cx0)-hw, int(cy0)-hh+4],float)  # template top-left in ref frame
res=[]
pred=None
for i in range(12,49):
    p=(tr[i]['cx'],tr[i]['cy']) if pred is None else pred
    if i in range(29,37):  # occluded region: predict from previous
        pass
    x0=int(p[0])-hw-25; y0=int(p[1])-hh-15+4
    S=G[i][y0:y0+2*hh+30, x0:x0+2*hw+50]
    r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,ml=cv2.minMaxLoc(r)
    # subpixel
    def sp(a,b,c): 
        d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
    yy,xx=ml[1],ml[0]
    dx=sp(r[yy,xx-1],r[yy,xx],r[yy,xx+1]) if 0<xx<r.shape[1]-1 else 0
    dy=sp(r[yy-1,xx],r[yy,xx],r[yy+1,xx]) if 0<yy<r.shape[0]-1 else 0
    off=np.array([x0+xx+dx, y0+yy+dy])-tc   # shift relative to ref
    c=np.array([cx0,cy0])+off
    res.append((i,c[0],c[1],mx))
    pred=(c[0]+16,c[1]+0.6)
for i,x,y,m in res: print(i,'%.2f %.2f  ncc=%.3f'%(x,y,m))
json.dump(res,open(D+'tm_%s_%d.json'%(v,ref),'w'))
