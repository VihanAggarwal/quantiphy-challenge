import json, numpy as np
d='/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/'
def load(v): return json.load(open(d+f'blobs_{v}.json'))
def track(v,cond):
    B=load(v); out={}
    for i,bl in enumerate(B):
        c=[b for b in bl if cond(b)]
        if c: out[i]=max(c,key=lambda b:b[4])
    return out
S=40.0
# bike x~908
for v in ['simulation_0070','simulation_0072','simulation_0073','simulation_0075']:
    T=track(v,lambda b: 900<b[0]<915 and b[2]<30 and b[3]>30)
    n=np.array(sorted(T)); cy=np.array([T[i][6] for i in n]); top=np.array([T[i][1] for i in n]); bot=np.array([T[i][1]+T[i][3] for i in n])
    m=(n>=1)&(top>2)
    print(v,'bike cy slope %.3f top slope %.3f bot slope %.3f px/fr'%(np.polyfit(n[m],cy[m],1)[0],np.polyfit(n[m],top[m],1)[0],np.polyfit(n[m],bot[m],1)[0]), 'len px med',np.median(bot-top))
# pedestrian x~1374.., small blob y~836
for v in ['simulation_0069','simulation_0071','simulation_0072','simulation_0075']:
    T=track(v,lambda b: b[0]>1300 and 820<b[1]<850 and b[4]<400)
    n=np.array(sorted(T)); cx=np.array([T[i][5] for i in n])
    p=np.polyfit(n,cx,1)
    w=(n>=12)&(n<=36); p2=np.polyfit(n[w],cx[w],1)
    print(v,'ped frames',len(n),n[0],n[-1],'slope %.3f px/fr, win12-36 %.3f -> %.3f m/s at %.1f px/m'%(p[0],p2[0],p2[0]*24/S,S))
# yellow car: big blob x>940 not van
for v in ['simulation_0068','simulation_0070','simulation_0071','simulation_0075']:
    T=track(v,lambda b: b[0]>940 and b[4]>10000)
    n=np.array(sorted(T)); cx=np.array([T[i][5] for i in n]); cy=np.array([T[i][6] for i in n])
    sp=np.hypot(np.diff(cx),np.diff(cy)); 
    print(v,'yellow centroid speed px/fr: f2-10 %.2f f20-40 %.2f f50-71 %.2f, f60 %.2f; mean f1-71 %.2f'%(sp[1:10].mean(),sp[19:40].mean(),sp[49:].mean(),sp[59],sp[0:].mean()))
    # end-to-end path length / time
    print('   path length f0..71 px %.1f, chord-based speed at 2.5s (f55-65) %.2f'%(sp.sum(), np.hypot(cx[65]-cx[55],cy[65]-cy[55])/10))
    b0=T[0];b71=T[71]
    print('   bbox f0',b0[:4],'f71',b71[:4])
