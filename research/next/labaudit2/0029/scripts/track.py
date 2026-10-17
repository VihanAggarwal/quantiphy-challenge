# ball centroid per video frame on o and x renders; ellipse fit to the x-render silhouette
import cv2, numpy as np, json
from frames import frames
out={}
for r in ['','x','s']:
    F=frames(r); res=[]
    for k,f in enumerate(F):
        hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
        m=cv2.inRange(hsv,(22,70,70),(45,255,255))
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: res.append(None); continue
        j=1+np.argmax(st[1:,4]); mm=(lab==j).astype(np.uint8)
        mm=cv2.morphologyEx(mm,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        cs,_=cv2.findContours(mm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=max(cs,key=cv2.contourArea)
        filled=np.zeros_like(mm); cv2.drawContours(filled,[c],-1,1,-1)
        ys,xs=np.nonzero(filled)
        e=cv2.fitEllipse(c) if len(c)>=5 else None
        res.append(dict(cx=float(xs.mean()),cy=float(ys.mean()),area=int(filled.sum()),
                        bbox=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
                        ell=[float(e[0][0]),float(e[0][1]),float(min(e[1])),float(max(e[1])),float(e[2])] if e else None))
    out[r or 'o']=res
json.dump(out,open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/track.json','w'))
o=out['o']; x=out['x']; s=out['s']
for k in range(len(o)):
    a=o[k]; b=x[k]; c=s[k]
    st=''
    if k>0 and a and o[k-1]:
        st='step %.1f'%np.hypot(a['cx']-o[k-1]['cx'],a['cy']-o[k-1]['cy'])
    print(k, 'o %.1f %.1f'%(a['cx'],a['cy']) if a else '-', 'x %.1f %.1f'%(b['cx'],b['cy']) if b else '-', 's %.1f %.1f'%(c['cx'],c['cy']) if c else '-',
          'xell minor %.1f major %.1f'%(b['ell'][2],b['ell'][3]) if b and b['ell'] else '', st)
