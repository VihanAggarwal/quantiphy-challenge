from common import *
import numpy as np, cv2, json
B=json.load(open(OUT+'ax_blobs.json'))
fs=frames('ax')
def alpha_img(f):
    b,g,r=[f[:,:,k].astype(float) for k in range(3)]
    ge=g-(r+b)/2
    a=1-(ge-20)/(252-20)
    return np.clip(a,0,1)
def ident(o):
    B_,G_,R_=o['bgr']
    return 'green' if (G_-B_)>45 else 'white'
rows=[]
for i in range(23,42):
    f=fs[i]; A=alpha_img(f)
    for o in B[str(i)]:
        if o['a']>1500 or o['y']>685: continue
        x,y=int(round(o['x'])),int(round(o['y']))
        h=40
        sub=A[y-h:y+h,x-h:x+h].copy()
        # restrict to the connected blob region dilated
        b,g,r=[f[y-h:y+h,x-h:x+h,k].astype(int) for k in range(3)]
        fg=(~((g>180)&(r<120)&(b<120))).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(fg,8)
        k=lab[h,h] if lab[h,h]>0 else np.argmax(st[1:,4])+1
        m=cv2.dilate((lab==k).astype(np.uint8),np.ones((5,5),np.uint8))
        w=sub*m
        yy,xx=np.mgrid[-h:h,-h:h]
        S=w.sum(); cx=(w*xx).sum()/S; cy=(w*yy).sum()/S
        cxx=(w*(xx-cx)**2).sum()/S; cyy=(w*(yy-cy)**2).sum()/S; cxy=(w*(xx-cx)*(yy-cy)).sum()/S
        ev,evec=np.linalg.eigh(np.array([[cxx,cxy],[cxy,cyy]]))
        smin,smaj=np.sqrt(ev)
        ang=np.degrees(np.arctan2(evec[1,1],evec[0,1]))
        Dmin=4*smin; L=np.sqrt(max(0,12*(smaj**2-smin**2)))
        rows.append(dict(i=i,obj=ident(o),x=x+cx,y=y+cy,area=S,eqd=2*np.sqrt(S/np.pi),Dmin=Dmin,L=L,ang=ang))
        print(i,ident(o),'c=(%.1f,%.1f) eqd=%.1f Dperp=%.1f blurL=%.1f ang=%.0f'%(x+cx,y+cy,2*np.sqrt(S/np.pi),Dmin,L,ang))
json.dump(rows,open(OUT+'ax_moments.json','w'))
