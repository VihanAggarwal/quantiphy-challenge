import json,numpy as np
def cap(n): return int(np.floor(25*n/24+0.5))
tr=json.load(open('tracks.json')); wd=json.load(open('widths.json'))
arcs={'B':[21,22,23,24,25,26,27],'C':[30,31,32,33,34,35],'D':[37,38,39,40,41,42],'E':[44,45,46,47,48]}
for src in ['s','x']:
    fits={}
    for k,fr in arcs.items():
        t=np.array([cap(n) for n in fr],float)
        u=np.array([tr[src][n]['cx'] for n in fr]); v=np.array([tr[src][n]['cy'] for n in fr])
        pv=np.polyfit(t,v,2); pu=np.polyfit(t,u,1)
        res=v-np.polyval(pv,t)
        apex_t=-pv[1]/(2*pv[0])
        fits[k]=(pv,pu)
        print(src,k,'acc_px/fr2=%.2f'%(2*pv[0]),'apex cap=%.2f v_apex=%.1f u_apex=%.1f'%(apex_t,np.polyval(pv,apex_t),np.polyval(pu,apex_t)),'du/dt=%.2f'%pu[0],'res',np.round(res,1))
    for a,b in [('B','C'),('C','D'),('D','E')]:
        d=fits[a][0]-fits[b][0]
        r=np.roots(d); r=r[np.isreal(r)].real
        # choose root between arcs
        tb=[x for x in r if 26<x<50]
        for x in tb:
            print('  bounce %s-%s cap=%.2f v=%.1f u_a=%.1f u_b=%.1f'%(a,b,x,np.polyval(fits[a][0],x),np.polyval(fits[a][1],x),np.polyval(fits[b][1],x)))
