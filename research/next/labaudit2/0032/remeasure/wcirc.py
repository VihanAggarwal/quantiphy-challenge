import cv2,numpy as np,json
def map_coordinates(g,c,order=1):
    return cv2.remap(g.astype(np.float32),np.asarray(c[1],np.float32).reshape(1,-1),np.asarray(c[0],np.float32).reshape(1,-1),cv2.INTER_LINEAR).ravel()
T=json.load(open('track_color.json'))
S={r['i']:r for r in json.load(open('wsize.json'))}
def fit_ellipse_axis(pts):
    # fit axis-aligned ellipse: A x^2 + B y^2 + C x + D y = 1
    x,y=pts[:,0],pts[:,1]
    M=np.c_[x*x,y*y,x,y]
    p,*_=np.linalg.lstsq(M,np.ones(len(x)),rcond=None)
    A,B,C,D=p
    x0=-C/(2*A); y0=-D/(2*B)
    G=1+A*x0*x0+B*y0*y0
    return x0,y0,np.sqrt(G/A),np.sqrt(G/B)
def fit_circle(pts):
    x,y=pts[:,0],pts[:,1]
    M=np.c_[x,y,np.ones(len(x))]
    p,*_=np.linalg.lstsq(M,-(x*x+y*y),rcond=None)
    x0=-p[0]/2;y0=-p[1]/2;r=np.sqrt(x0*x0+y0*y0-p[2]); return x0,y0,r
out={}
for i in range(32,49):
    img=cv2.imread('frames/f%02d.png'%i)
    g=cv2.GaussianBlur(cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(float),(0,0),0.8)
    if i in S: x0,y0=S[i]['cx'],S[i]['cy']
    else: x0,y0=T[i]['w'][:2]
    for it in range(3):
        pts=[];angs=[]
        for a in np.deg2rad(np.arange(0,360,7.5)):
            rr=np.arange(4,22,0.25)
            xs=x0+rr*np.cos(a); ys=y0+rr*np.sin(a)
            prof=map_coordinates(g,[ys,xs],order=1)
            d=np.gradient(prof)
            k=np.argmin(d)  # strongest bright->dark going outward
            if d[k]<-4:
                pts.append((xs[k],ys[k])); angs.append(np.rad2deg(a))
        pts=np.array(pts); angs=np.array(angs)
        # exclude bottom sector (shadow/contact) 60..120 deg (image y down) -> keep for now separately
        keep=~((angs>45)&(angs<135))
        cx,cy,r=fit_circle(pts[keep])
        x0,y0=cx,cy
    ex=fit_ellipse_axis(pts[keep])
    cxa,cya,ra=fit_circle(pts)
    out[i]=dict(cx=cx,cy=cy,r=r,ex=ex[0],ey=ex[1],ea=ex[2],eb=ex[3],cx_all=cxa,cy_all=cya,r_all=ra,n=int(keep.sum()))
    print(i,' '.join('%s=%.2f'%(k,v) for k,v in out[i].items()))
json.dump(out,open('wcirc.json','w'))
