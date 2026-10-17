# Vertical vanishing point from locker seams / pole in the median background of render a
import cv2, numpy as np
m=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit2/0035/rm2/frames/a_median.png')
g=cv2.cvtColor(m,cv2.COLOR_BGR2GRAY).astype(np.float32)
hp=g-cv2.GaussianBlur(g,(0,0),15)
hp=cv2.GaussianBlur(hp,(0,0),2)
def trace(x0,x1,y0,y1,yA,yB):
    # expected line from (x0,yA) to (x1,yB); search +-15 px for darkest ridge each row
    pts=[]
    for y in range(y0,y1,4):
        xe=x0+(x1-x0)*(y-yA)/(yB-yA)
        lo=int(xe-15); hi=int(xe+15)
        row=hp[y,lo:hi]
        k=int(np.argmin(row))
        if 2<=k<len(row)-2:
            # subpixel parabola
            a,b,c=row[k-1],row[k],row[k+1]; dk=0.5*(a-c)/(a-2*b+c) if (a-2*b+c)!=0 else 0
            pts.append((lo+k+dk,y,row[k]))
    pts=np.array(pts)
    p=np.polyfit(pts[:,1],pts[:,0],1)
    res=pts[:,0]-np.polyval(p,pts[:,1])
    return p,res.std(),len(pts)
lines={'A':trace(37,119,20,280,0,300),'B':trace(240,275,20,240,0,260),'pole':trace(650,650,70,230,0,300)}
for k,(p,s,n) in lines.items(): print(k,'x = %.4f*y + %.1f'%(p[0],p[1]),'resid %.2f n %d'%(s,n))
def inter(p,q):
    y=(q[1]-p[1])/(p[0]-q[0]); return np.polyval(p,y),y
f=711.;cy=360.;cx=640.
for a,b in (('A','B'),('A','pole'),('B','pole')):
    x,y=inter(lines[a][0],lines[b][0])
    # pitch from VP: direction K^-1 (x,y,1); angle between it and optical axis
    d=np.array([(x-cx)/f,(y-cy)/f,1.]); d/=np.linalg.norm(d)
    print(a,b,'VP (%.0f,%.0f)  pitch(deg)=%.1f'%(x,y,90-np.degrees(np.arccos(d[2]))))
