import json,numpy as np
f=711.0; cx,cy=640.0,360.0; D=0.040
W=json.load(open('wrad.json'))
ks=list(range(36,49))
cap=lambda k: k+2 if k>=36 else (k+1 if k>=12 else k)
def P3(variant):
    rows=[]
    for k in ks:
        x,y,r=W[str(k)][variant][:3]; d=2*r
        rows.append((cap(k),x,y,d))
    return np.array(rows)
for variant in [0,1,2]:
    A=P3(variant); c,x,y,d=A.T; t=c/25
    # regression y vs d -> horizon & hc
    s,b=np.polyfit(d,y,1)
    print('variant',variant,'y=%.3f*d+%.2f -> y_h=%.1f hc=%.3f'%(s,b,b,s*D))
    # route S: size-based
    Z=f*D/d; X=(x-cx)*Z/f; Y=(y-cy)*Z/f
    Pc=np.c_[X,Y,Z]
    # range of surface pt
    u=np.c_[(x-cx)/f,(y-cy)/f,np.ones_like(x)]; u/=np.linalg.norm(u,axis=1)[:,None]
    R=np.linalg.norm(Pc,axis=1)
    Pl=(R-D/2)[:,None]*u
    for name,P in [('centre',Pc),('label-surface',Pl)]:
        # raw forward diff at capture 40->41
        i40=list(c).index(40); i41=list(c).index(41)
        raw=np.linalg.norm(P[i41]-P[i40])*25*100
        # linear fit over capture 38..50
        out=[]
        for lo,hi,deg in [(38,50,1),(38,50,2),(38,44,1),(38,46,2)]:
            m=(c>=lo)&(c<=hi)
            V=[]
            for j in range(3):
                p=np.polyfit(t[m],P[m,j],deg)
                V.append(np.polyval(np.polyder(p),40.5/25))
            out.append('%d-%d deg%d: %.1f (vx %.1f vy %.1f vz %.1f)'%(lo,hi,deg,np.linalg.norm(V)*100,V[0]*100,V[1]*100,V[2]*100))
        print('  route S',name,'raw fwd 40->41 %.1f cm/s |'%raw,' | '.join(out))
    print('  Z per frame',dict(zip(c.astype(int),Z.round(3))))
