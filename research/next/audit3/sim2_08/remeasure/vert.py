from util import *
F=frames('0259'); g=F[0].astype(float).mean(2)
gx=cv2.Sobel(cv2.GaussianBlur(g,(0,0),1.0),cv2.CV_64F,1,0,ksize=3)
# for x-ranges, find strongest edge per row band, subpixel
def edge_track(x0,x1,ys,sign):
    out=[]
    for y in ys:
        prof=gx[y-3:y+4,x0:x1].mean(0)*sign
        i=int(np.argmax(prof))
        if 0<i<len(prof)-1:
            a,b,c=prof[i-1],prof[i],prof[i+1]; d=0.5*(a-c)/(a-2*b+c)
        else: d=0
        out.append((y,x0+i+d,prof[i]))
    return out
np.set_printoptions(linewidth=200)
# print a row profile to find candidate edges
print(np.round(g[400,1600:1780:2]).astype(int))
print(np.round(g[100,1600:1780:2]).astype(int))
print(np.round(g[700,1600:1780:2]).astype(int))
for (x0,x1,s,name) in [(1748,1768,1,'rise~1756'),(1722,1740,-1,'fall~1731')]:
    R=edge_track(x0,x1,range(40,800,40),s)
    ys=np.array([r[0] for r in R]); xs=np.array([r[1] for r in R])
    p=np.polyfit(ys,xs,1)
    print(name,np.round(xs,2),' slope dx/dy=%.5f rms=%.2f'%(p[0],(xs-np.polyval(p,ys)).std()))
# AC left edge (x~132) rows 770-1070
R=edge_track(120,145,range(780,1075,15),1); xs=np.array([r[1] for r in R]); ys=np.array([r[0] for r in R])
print('AC left',np.round(xs,2)); p=np.polyfit(ys,xs,1); print(' slope %.5f'%p[0])
R=edge_track(120,145,range(780,1075,15),-1); xs=np.array([r[1] for r in R]);print('AC left neg',np.round(xs,2)); p=np.polyfit(ys,xs,1); print(' slope %.5f'%p[0])
