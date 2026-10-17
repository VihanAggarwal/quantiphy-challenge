import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0031.mp4')
F=[]
while True:
    ok,x=c.read()
    if not ok: break
    F.append(cv2.cvtColor(x,cv2.COLOR_BGR2GRAY).astype(np.float32))
E=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/edge_a.json'))
def match(k,b,half):
    cx,cy,r=E[k][b][:3]; cx2,cy2,r2=E[k+1][b][:3]
    s=r2/r
    h=int(round(r*0.85))
    tpl=F[k][int(cy)-h:int(cy)+h+1,int(cx)-h:int(cx)+h+1]
    # scale template to next-frame size about its centre
    tpl=cv2.resize(tpl,None,fx=s,fy=s,interpolation=cv2.INTER_LINEAR)
    sx0=int(cx)-h-12; sy0=int(cy)-h-12
    srch=F[k+1][sy0:sy0+tpl.shape[0]+24+int(4*s), sx0:sx0+tpl.shape[1]+24+int(4*s)]
    res=cv2.matchTemplate(srch,tpl,cv2.TM_CCOEFF_NORMED)
    _,mx,_,ml=cv2.minMaxLoc(res)
    x,y=ml
    # subpixel parabola
    def sp(a,b_,c_): d=a-2*b_+c_; return 0 if d==0 else 0.5*(a-c_)/d
    dx=sp(res[y,x-1],res[y,x],res[y,x+1]) if 0<x<res.shape[1]-1 else 0
    dy=sp(res[y-1,x],res[y,x],res[y+1,x]) if 0<y<res.shape[0]-1 else 0
    # template centre in next frame
    ncx=sx0+x+dx+(tpl.shape[1]-1)/2; ncy=sy0+y+dy+(tpl.shape[0]-1)/2
    ocx=int(cx)-h+(2*h)/2; ocy=int(cy)-h+(2*h)/2
    return ncx-ocx, ncy-ocy, mx
print(' k->k+1   tennis(du,dv,|d|,score)        white(du,dv,|d|,score)')
for k in range(16,47):
    s='%2d->%2d'%(k,k+1)
    for b in 't','w':
        if b in E[k] and b in E[k+1] and (b=='w' or k<41):
            du,dv,sc=match(k,b,0); s+='   %6.2f %6.2f %5.2f %.3f'%(du,dv,np.hypot(du,dv),sc)
        else: s+='   '+' '*26
    print(s)
