import cv2, numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
r=sys.argv[1]; key=sys.argv[2]
T=json.load(open(d+'track_x.json'))
def crossings(p, lvl_lo, lvl_hi, c):
    # p: profile, c: centre index; find first crossing going outwards on each side at level midway between interior and outside
    inner=np.median(p[c-2:c+3])
    res=[]
    for direction,lvl in [(-1,lvl_lo),(1,lvl_hi)]:
        i=c
        out_val=None
        while 0<i<len(p)-1:
            j=i+direction
            if p[j] < (inner+lvl)/2 <= p[i]:
                # interpolate
                frac=(p[i]-(inner+lvl)/2)/(p[i]-p[j]); res.append(i+direction*frac); break
            i=j
        else: res.append(np.nan)
    return res, inner
for i in range(int(sys.argv[3]),int(sys.argv[4])):
    im=cv2.imread(d+'frames/%s_%02d.png'%(r,i))
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float) if key=='wht' else cv2.cvtColor(im,cv2.COLOR_BGR2HSV)[...,1].astype(float)
    t=T[str(i)][key]
    if t is None: continue
    cx,cy=int(round(t['cx'])),int(round(t['cy']))
    # vertical profile averaged over 3 columns
    vp=g[:,cx-1:cx+2].mean(axis=1)
    hp=g[cy-1:cy+2,:].mean(axis=0)
    # outside levels: take value 25 px away
    (top,bot),inn=crossings(vp, vp[cy-30], vp[cy+30], cy)
    (lft,rgt),_=crossings(hp, hp[cx-40], hp[cx+40], cx)
    print(i,'centre(%.1f,%.1f)'%((lft+rgt)/2,(top+bot)/2),'V=%.1f H=%.1f'%(bot-top,rgt-lft),'inner %.0f out_top %.0f out_bot %.0f'%(inn,vp[cy-30],vp[cy+30]))
