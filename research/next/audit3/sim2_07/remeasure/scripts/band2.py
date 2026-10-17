import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0254.mp4')
fr=[]
for i in range(12):
    ok,f=c.read(); fr.append(f)
bg=np.median(np.stack(fr),axis=0).astype(np.float32)
Y=bg@np.array([0.114,0.587,0.299],np.float32)
Y=cv2.GaussianBlur(Y,(0,0),1.0)
th=np.radians(44.224); d=np.array([np.cos(th),np.sin(th)]); n=np.array([-d[1],d[0]])
p0=np.array([649.6,331.56])
E1=[];E2=[]
for sv in np.arange(-640,1060,10):
    c0=p0+sv*d
    if not (5<c0[0]<1915 and 5<c0[1]<1075): continue
    r=np.arange(-30,55,0.25)
    prof=np.mean([cv2.remap(Y,(c0[0]+r*n[0]+k*d[0]).astype(np.float32).reshape(1,-1),(c0[1]+r*n[1]+k*d[1]).astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0] for k in range(-4,5)],axis=0)
    g=np.gradient(prof,r)
    m1=(r>-25)&(r<0); m2=(r>20)&(r<50)
    j1=np.where(m1)[0][np.argmin(g[m1])]; j2=np.where(m2)[0][np.argmax(g[m2])]
    def sub(j):
        y0,y1,y2=g[j-1],g[j],g[j+1]; den=y0-2*y1+y2
        return r[j]+(0.5*(y0-y2)/den if den!=0 else 0)*(r[1]-r[0])
    E1.append((sv,sub(j1),g[j1])); E2.append((sv,sub(j2),g[j2]))
E1=np.array(E1);E2=np.array(E2)
for nm,E in (('upper(r<0)',E1),('lower(r>0)',E2)):
    p=np.polyfit(E[:,0],E[:,1],1); res=E[:,1]-np.polyval(p,E[:,0])
    print(nm,'slope dr/ds=%.5f intercept=%.2f rms=%.2f n=%d meangrad=%.1f'%(p[0],p[1],res.std(),len(E),E[:,2].mean()))
p1=np.polyfit(E1[:,0],E1[:,1],1); p2=np.polyfit(E2[:,0],E2[:,1],1)
# width w(s)=p2(s)-p1(s); zero at s_vp
w=lambda s: np.polyval(p2,s)-np.polyval(p1,s)
svp=-(p2[1]-p1[1])/(p2[0]-p1[0])
print('band width at s=-640,0,1000:',w(-640),w(0),w(1000),' VP at s(rel p0)=',svp,' abs s=',svp+p0@d)
# also ball path line relative: ball path r=0 by construction; distance of VP from line via each edge
print('edge1 hits r=0 at s=',-p1[1]/p1[0],' edge2 hits r=0 at s=',-p2[1]/p2[0])
