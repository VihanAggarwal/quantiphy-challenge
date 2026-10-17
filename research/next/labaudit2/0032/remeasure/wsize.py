import cv2,numpy as np,json
T=json.load(open('track_color.json'))
def cross(p,thr,start,step):
    i=start
    while 0<=i+step<len(p):
        if (p[i]-thr)*(p[i+step]-thr)<=0:
            return i+step*(p[i]-thr)/(p[i]-p[i+step])
        i+=step
    return None
out=[]
for i in range(33,49):
    img=cv2.imread('frames/f%02d.png'%i)
    g=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(float)
    x0,y0=T[i]['w'][:2]
    X,Y=int(round(x0)),int(round(y0))
    # iterate: refine centre
    for it in range(3):
        X,Y=int(round(x0)),int(round(y0))
        vprof=g[Y-30:Y+31,X-2:X+3].mean(1)   # vertical profile
        hprof=g[Y-2:Y+3,X-35:X+36].mean(0)
        peak=np.percentile(g[Y-4:Y+5,X-4:X+5],80)
        bg_t=np.median(g[Y-30:Y-20,X-5:X+6]); bg_b=np.median(g[Y+20:Y+28,X-5:X+6])
        bg_l=np.median(g[Y-3:Y+4,X-35:X-25]); bg_r=np.median(g[Y-3:Y+4,X+25:X+35])
        top=cross(vprof,(peak+bg_t)/2,30,-1); bot=cross(vprof,(peak+bg_b)/2,30,1)
        lef=cross(hprof,(peak+bg_l)/2,35,-1); rig=cross(hprof,(peak+bg_r)/2,35,1)
        yt=Y-30+top; yb=Y-30+bot; xl=X-35+lef; xr=X-35+rig
        x0n=(xl+xr)/2; y0n=(yt+yb)/2
        x0,y0=x0n,y0n
    r=dict(i=i,cx=x0,cy=y0,dv=yb-yt,dh=xr-xl,yt=yt,yb=yb,xl=xl,xr=xr,peak=peak,bgt=bg_t,bgb=bg_b)
    out.append(r)
    print(' '.join('%s=%.2f'%(k,v) for k,v in r.items()))
json.dump(out,open('wsize.json','w'))
