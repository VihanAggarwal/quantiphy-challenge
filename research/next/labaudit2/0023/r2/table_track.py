import cv2, numpy as np, json, sys
from geo import *
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
def cap(k): return k if k<=11 else (k+1 if k<=35 else k+2)
def parab(p,i):
    if 0<i<len(p)-1:
        a,b,c=p[i-1],p[i],p[i+1]; den=a-2*b+c
        return i+(0.5*(a-c)/den if den!=0 else 0)
    return float(i)
def measure(pre,k,xs=range(512,642,4)):
    im=cv2.imread(R1+f'{pre}{k:02d}.png').astype(float)
    lum=im.mean(2); mn=im.min(2)
    out=[]
    for x in xs:
        col=lum[455:530,x-1:x+2].mean(1); cm=mn[455:530,x-1:x+2].mean(1)
        # top edge: white board -> cover: first crossing of min-channel below 232 after being >240
        j=np.nonzero(cm>240)[0]
        if len(j)==0: continue
        st=j[0]
        kk=np.nonzero(cm[st:]<232)[0]
        if len(kk)==0: continue
        i=st+kk[0]; ytop=455+i-1+(cm[i-1]-232)/(cm[i-1]-cm[i])
        # cover front edge dark line: argmin of lum in [ytop+6, ytop+22]
        a=int(ytop-455)+6; seg=col[a:a+16]; i1=np.argmin(seg); yd=455+a+parab(seg,i1)
        # bottom: table rows are R-B large; find last row where book (cream/dark) before table; use lum minimum in [yd+6,yd+22] (contact shadow)
        a2=int(yd-455)+6; seg2=col[a2:a2+18]; i2=np.argmin(seg2); yb=455+a2+parab(seg2,i2)
        out.append((x,ytop,yd,yb,seg[i1],seg2[i2]))
    return np.array(out)
h0=float(sys.argv[1]) if len(sys.argv)>1 else 0.170
Hb=0.0146
res={}
for pre in ['o','x','s']:
    rows=[]
    for k in range(32,47):
        M=measure(pre,k)
        if len(M)==0: continue
        # 3D: bottom line on table (height 0 -> camera height h0), front cover edge at height Hb, top (back) edge at Hb
        Pb=np.array([table_pt(x,yb,h0) for x,_,_,yb,_,_ in M]); Pd=np.array([table_pt(x,yd,h0-Hb) for x,_,yd,_,_,_ in M]); Pt=np.array([table_pt(x,yt,h0-Hb) for x,yt,_,_,_,_ in M])
        W_cov=np.median(np.linalg.norm(Pt-Pd,axis=1))*100
        rows.append(dict(k=k,c=cap(k),ytop=np.median(M[:,1]),yd=np.median(M[:,2]),yb=np.median(M[:,3]),Zb=np.median(Pb[:,2]),Zd=np.median(Pd[:,2]),Zt=np.median(Pt[:,2]),W=W_cov,n=len(M)))
    res[pre]=rows
    print('==',pre,'h=%.3f'%h0)
    prev=None
    for r in rows:
        s=''
        if prev:
            dc=r['c']-prev['c']
            s='  dZ/step(cm per capture frame): bot %.2f front %.2f back %.2f -> speed %.0f/%.0f/%.0f cm/s'%tuple([(prev[q]-r[q])*100/dc for q in ['Zb','Zd','Zt']]+[(prev[q]-r[q])*2500/dc for q in ['Zb','Zd','Zt']])
        print('v%d c%d ytop %.1f ydark %.1f ybot %.1f | Zbot %.4f Zfront %.4f Zback %.4f Wcover %.1f n%d'%(r['k'],r['c'],r['ytop'],r['yd'],r['yb'],r['Zb'],r['Zd'],r['Zt'],r['W'],r['n'])+s)
        prev=r
json.dump(res,open('table_track_h%.3f.json'%h0,'w'),default=float)
