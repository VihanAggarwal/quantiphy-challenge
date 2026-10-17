import json, numpy as np
d='/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/'
def load(v): return json.load(open(d+f'blobs_{v}.json'))
def pick(bl, cond):
    c=[b for b in bl if cond(b)]
    return max(c,key=lambda b:b[4]) if c else None
# van: x~788, w~88
for v in ['simulation_0068','simulation_0069','simulation_0073','simulation_0075']:
    B=load(v)
    n=[];top=[];bot=[];cy=[]
    for i,bl in enumerate(B):
        b=pick(bl,lambda b: 780<b[0]<800 and b[2]>80 and b[3]>200)
        if b is None: continue
        if b[1]<=2 or b[1]+b[3]>=1078: continue
        n.append(i);top.append(b[1]);bot.append(b[1]+b[3]);cy.append(b[6])
    n=np.array(n);top=np.array(top,float);bot=np.array(bot,float);cy=np.array(cy)
    m=n>=2
    for name,y in (('top',top),('bot',bot),('cy',cy)):
        p=np.polyfit(n[m],y[m],2)
        print(v,name,'acc px/s2=%.1f'%(-2*p[0]*576),'vertex n=%.2f'%(-p[1]/(2*p[0])),'rms=%.2f'%np.std(np.polyval(p,n[m])-y[m]))
    print(v,'van blob h median',np.median(bot-top), 'frames',n[0],n[-1])
