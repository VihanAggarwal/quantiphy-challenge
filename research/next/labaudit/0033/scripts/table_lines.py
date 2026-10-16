import cv2, numpy as np, json
g=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit/0033/frames/x_42.png')
gray=cv2.cvtColor(g,cv2.COLOR_BGR2GRAY).astype(float)
m=gray>25
# far edge: top boundary per column
far=[]
for x in range(490,740,5):
    col=m[380:470,x]; y=np.argmax(col)+380
    # subpixel: half-level crossing
    v=gray[380:470,x]; 
    k=y-380; y0=k-1; 
    lv=(v[k-3]+v[k+4])/2
    # find crossing
    for j in range(k-4,k+4):
        if v[j]<lv<=v[j+1]: ys=j+(lv-v[j])/(v[j+1]-v[j])+380; break
    far.append((x,ys))
left=[];right=[]
for y in range(445,512,3):
    row=gray[y,:]; xs=np.where(row>25)[0]; xs=xs[(xs>250)&(xs<1000)]
    xl=xs.min(); xr=xs.max()
    lv=(row[xl-4]+row[xl+4])/2
    for j in range(xl-4,xl+4):
        if row[j]<lv<=row[j+1]: xl2=j+(lv-row[j])/(row[j+1]-row[j]); break
    lv=(row[xr-4]+row[xr+4])/2
    for j in range(xr-4,xr+4):
        if row[j]>=lv>row[j+1]: xr2=j+(row[j]-lv)/(row[j]-row[j+1]); break
    left.append((xl2,y)); right.append((xr2,y))
# near edge of top surface: strongest negative vertical gradient (bright top -> darker band) per column in 495..545
sm=cv2.GaussianBlur(gray,(0,0),1.0)
gy=np.diff(sm,axis=0)
near=[]
for x in range(340,880,10):
    # expected y roughly linear between (304,518) and (909,534)
    ye=518+(x-304)*(16/605)
    lo=int(ye-10); hi=int(ye+10)
    seg=gy[lo:hi,x]; k=np.argmin(seg)
    near.append((x,lo+k+0.5,seg[k]))
def fitline(pts,vertical=False):
    p=np.array(pts)[:,:2]
    if vertical: a,b=np.polyfit(p[:,1],p[:,0],1); res=p[:,0]-(a*p[:,1]+b); return ('x=a*y+b',a,b,res.std())
    a,b=np.polyfit(p[:,0],p[:,1],1); res=p[:,1]-(a*p[:,0]+b); return ('y=a*x+b',a,b,res.std())
for name,pts,v in [('far',far,False),('left',left,True),('right',right,True),('near',near,False)]:
    print(name,fitline(pts,v))
print('near pts',[(x,round(y,1),round(s,1)) for x,y,s in near])
def L_h(a,b): return np.array([a,-1,b])   # a x - y + b =0
def L_v(a,b): return np.array([-1,a,b])   # -x + a y + b =0
F=L_h(*fitline(far)[1:3]); N=L_h(*fitline([(x,y) for x,y,s in near])[1:3])
Lf=L_v(*fitline(left,True)[1:3]); R=L_v(*fitline(right,True)[1:3])
def X(l1,l2): p=np.cross(l1,l2); return p[:2]/p[2]
C={'FL':X(F,Lf).tolist(),'FR':X(F,R).tolist(),'NL':X(N,Lf).tolist(),'NR':X(N,R).tolist()}
print(C)
json.dump(C,open('/home/user/quantiphy-challenge/research/next/labaudit/0033/corners.json','w'),indent=1)
