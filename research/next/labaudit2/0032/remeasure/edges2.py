import cv2,numpy as np,json
# average several static frames (camera static) to reduce noise: use frames 0..20 (balls static, table clear except balls at far edge)
acc=None
for i in range(0,21):
    im=cv2.imread('frames/f%02d.png'%i).astype(float)
    acc=im if acc is None else acc+im
img=(acc/21).astype(np.uint8)
cv2.imwrite('static_mean.png',img)
lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(float)
L,b=lab[...,0],lab[...,2]
def edge_rows(xlo,xhi,ys,ch,sign):
    pts=[]
    for y in ys:
        p=ch[y,xlo:xhi]
        d=np.diff(p)*sign
        k=np.argmax(d)
        if 0<k<len(d)-1:
            # parabolic subpixel
            a,b_,c=d[k-1],d[k],d[k+1]
            off=0.5*(a-c)/(a-2*b_+c) if (a-2*b_+c)!=0 else 0
            pts.append((xlo+k+0.5+off,y,d[k]))
    return np.array(pts)
def edge_cols(ylo,yhi,xs,ch,sign):
    pts=[]
    for x in xs:
        p=ch[ylo:yhi,x]; d=np.diff(p)*sign; k=np.argmax(d)
        if 0<k<len(d)-1:
            a,b_,c=d[k-1],d[k],d[k+1]
            off=0.5*(a-c)/(a-2*b_+c) if (a-2*b_+c)!=0 else 0
            pts.append((x,ylo+k+0.5+off,d[k]))
    return np.array(pts)
res={}
for name,ch in [('b',b),('L',L)]:
    # left edge: wall (low b) -> table (high b) going right
    le=[];re=[]
    for y in range(436,481):
        # predicted x from rough fit
        xl=int(-1.8768*y+1369.93); xr=int(1.6257*y+150.15)
        e=edge_rows(xl-8,xl+9,[y],ch,+1); 
        if len(e): le.append(e[0])
        e=edge_rows(xr-8,xr+9,[y],ch,-1)
        if len(e): re.append(e[0])
    le=np.array(le); re=np.array(re)
    pl=np.polyfit(le[:,1],le[:,0],1); pr=np.polyfit(re[:,1],re[:,0],1)
    print(name,'left',pl,'rms',np.std(le[:,0]-np.polyval(pl,le[:,1])).round(2),'right',pr,'rms',np.std(re[:,0]-np.polyval(pr,re[:,1])).round(2))
    print(' right resid',(re[:,0]-np.polyval(pr,re[:,1])).round(1))
    print(' left resid',(le[:,0]-np.polyval(pl,le[:,1])).round(1))
    res[name]=(pl,pr)
# near edge: L drop top->band going down
ne=edge_cols(470,505,list(range(480,945,3)),L,-1)
pn=np.polyfit(ne[:,0],ne[:,1],1); print('near',pn,'rms',np.std(ne[:,1]-np.polyval(pn,ne[:,0])).round(2))
fe=edge_cols(415,440,list(range(566,634,2))+list(range(800,846,2)),b,+1)
pf=np.polyfit(fe[:,0],fe[:,1],1); print('far',pf,'rms',np.std(fe[:,1]-np.polyval(pf,fe[:,0])).round(2))
print(' far pts',fe[:,:2].round(1).tolist())
json.dump({'left_b':res['b'][0].tolist(),'right_b':res['b'][1].tolist(),'left_L':res['L'][0].tolist(),'right_L':res['L'][1].tolist(),'near':pn.tolist(),'far':pf.tolist()},open('edges2.json','w'))
