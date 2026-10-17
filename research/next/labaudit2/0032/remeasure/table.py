import cv2,numpy as np,json
img=cv2.imread('frames/f48.png')
lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(float)
L,b=lab[...,0],lab[...,2]
m=((b>136)&(L>95)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,cc,st,_=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); m=(cc==k)
print('table comp bbox',st[k])
cv2.imwrite('tmask.png',(m*255).astype(np.uint8)[380:520,420:1000])
# subpixel transitions using b channel threshold crossing (smooth)
bs=cv2.GaussianBlur(b,(0,0),1.0)
def cross(prof,thr):
    # first index where prof crosses thr, linear interp
    for i in range(len(prof)-1):
        if (prof[i]-thr)*(prof[i+1]-thr)<=0 and prof[i]!=prof[i+1]:
            return i+(thr-prof[i])/(prof[i+1]-prof[i])
    return None
thr=136
left=[];right=[]
for y in range(440,480):
    xs=np.where(m[y])[0]
    if len(xs)==0: continue
    xl=xs.min(); xr=xs.max()
    p=bs[y,xl-6:xl+6]; c=cross(p,thr); 
    if c is not None: left.append((xl-6+c,y))
    p=bs[y,xr-6:xr+6]; c=cross(p,thr)
    if c is not None: right.append((xr-6+c,y))
Ls=cv2.GaussianBlur(L,(0,0),1.0)
near=[]
for x in range(490,940,2):
    ys=np.where(m[:,x])[0]; yb=ys.max()
    p=Ls[yb-5:yb+6,x]; c=cross(p,(Ls[yb-4,x]+Ls[yb+5,x])/2)
    if c is not None: near.append((x,yb-5+c))
far=[]
for x in list(range(565,632,2))+list(range(800,850,2)):
    ys=np.where(m[:,x])[0]; yt=ys.min()
    p=bs[yt-6:yt+6,x]; c=cross(p,thr)
    if c is not None: far.append((x,yt-6+c))
def fitxy(pts,vert):
    a=np.array(pts,float)
    if vert: # x = p*y+q
        p=np.polyfit(a[:,1],a[:,0],1); r=a[:,0]-np.polyval(p,a[:,1])
    else:
        p=np.polyfit(a[:,0],a[:,1],1); r=a[:,1]-np.polyval(p,a[:,0])
    return p,r.std()
pl,sl=fitxy(left,True); pr,sr=fitxy(right,True); pn,sn=fitxy(near,False); pf,sf=fitxy(far,False)
print('left x=%.4f y+%.2f rms %.2f n=%d'%(pl[0],pl[1],sl,len(left)))
print('right x=%.4f y+%.2f rms %.2f n=%d'%(pr[0],pr[1],sr,len(right)))
print('near y=%.4f x+%.2f rms %.2f'%(pn[0],pn[1],sn))
print('far y=%.4f x+%.2f rms %.2f'%(pf[0],pf[1],sf), far[:5], far[-5:])
def inter(pv,ph):
    # x=a y + b ; y = c x + d
    a,b_=pv; c,d=ph
    y=(c*b_+d)/(1-a*c); x=a*y+b_; return [x,y]
C={'NL':inter(pl,pn),'NR':inter(pr,pn),'FL':inter(pl,pf),'FR':inter(pr,pf)}
print(C)
json.dump(C,open('table_corners.json','w'))
