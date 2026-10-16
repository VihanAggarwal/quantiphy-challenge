# Route A: ranges from apparent horizontal width (scaled to the stated range at f36), centres from tracker; compare with route B
import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
G=np.load(d+'plane711.npy',allow_pickle=True).item(); n=-G['n']
f=711.; Ki=np.linalg.inv(np.array([[f,0,640],[0,f,360],[0,0,1.]]))
def ray(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
def width(r,i,cx,cy,chan):
    im=cv2.imread(d+'frames/%s_%02d.png'%(r,i))
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float) if chan=='g' else cv2.cvtColor(im,cv2.COLOR_BGR2HSV)[...,1].astype(float)
    cx,cy=int(round(cx)),int(round(cy))
    ws=[]
    for yy in range(cy-2,cy+1):
        hp=g[yy,:]
        inner=np.median(hp[cx-2:cx+3]); 
        edges=[]
        for dirn in (-1,1):
            out=hp[cx+dirn*45]; lvl=(inner+out)/2; i0=cx
            while True:
                j=i0+dirn
                if (hp[j]-lvl)*(hp[i0]-lvl)<=0:
                    edges.append(i0+dirn*(hp[i0]-lvl)/(hp[i0]-hp[j])); break
                i0=j
        ws.append(edges[1]-edges[0])
    return np.median(ws)
for r in ['x','o']:
  T=json.load(open(d+'track_x.json'))
  for name,key,R36,rad,chan in [('ping','wht',1.353,0.02,'g'),('tennis','yel',1.183,0.0335,'s')]:
    fr=list(range(36,49)) if key=='wht' else list(range(33,41))
    W={i:width(r,i,T[str(i)][key]['cx'],T[str(i)][key]['cy'],chan) for i in fr}
    # lateral pixel speed -> blur estimate unknown; use raw widths and widths minus k*|dx|
    dx={i:abs(T[str(i+1)][key]['cx']-T[str(i)][key]['cx']) if str(i+1) in T and T[str(i+1)][key] else np.nan for i in fr}
    print('==',r,name,' widths:',' '.join('%d:%.1f'%(i,W[i]) for i in fr))
    for blurk in [0.0,0.5]:
        We={i:W[i]-blurk*dx[i] for i in fr if not np.isnan(dx[i])}
        R={i:R36*We[36]/We[i] for i in We}
        XA={i:R[i]*ray((T[str(i)][key]['cx'],T[str(i)][key]['cy'])) for i in R}
        h=0.173
        XB={i:ray((T[str(i)][key]['cx'],T[str(i)][key]['cy']))*(h-rad)/(n@ray((T[str(i)][key]['cx'],T[str(i)][key]['cy']))) for i in R}
        ks=sorted(R)
        # linear fit speeds over windows
        def fitspeed(X,a,b):
            ii=[i for i in ks if a<=i<=b]; A=np.array([X[i] for i in ii]); t=np.array(ii)/24.
            v=np.polyfit(t,A,1)[0]; return 100*np.linalg.norm(v)
        wins=[(36,40),(36,42),(37,43),(36,47)] if key=='wht' else [(33,36),(36,39),(34,39)]
        print('  blur k=%.1f'%blurk,'R:',' '.join('%d:%.3f'%(i,R[i]) for i in ks))
        print('    route A fit speeds',['%s:%.1f'%(w,fitspeed(XA,*w)) for w in wins])
        print('    route B fit speeds',['%s:%.1f'%(w,fitspeed(XB,*w)) for w in wins])
