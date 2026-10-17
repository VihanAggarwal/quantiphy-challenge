"""Associate x-render components to the 4 objects and fit free-fall in capture time."""
import json, numpy as np, math
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b'
X=json.load(open(f'{OUT}/xcomps.json'))
def cap(v):  # video frame -> clip capture index (ffmpeg fps 25->24, half-up)
    return math.floor(v*25/24+0.5)
tracks={'tennis':{},'pineapple':{},'soccer':{},'box':{}}
for i in range(28,49):
    for c in X[str(i)]:
        x,y=c['c']; hue=c['hue']; sat=c['sat']
        if 30<=hue<=40 and 700<x<800 and c['a']<1200: tracks['tennis'][i]=c
        elif 20<=hue<=30 and sat>80 and x>800: tracks['pineapple'][i]=c
        elif x>505 and x<600 and sat<20: tracks['soccer'][i]=c
        elif x<505 and sat<25 and c['a']>1000: tracks['box'][i]=c
json.dump({k:{str(i):v for i,v in d.items()} for k,d in tracks.items()},open(f'{OUT}/xtracks.json','w'))
for k,d in tracks.items():
    print(k)
    for i,c in sorted(d.items()):
        print('  v%02d cap%02d'%(i,cap(i)), [round(t,1) for t in c['c']], 'wh',c['bb'][2]-c['bb'][0]+1,c['bb'][3]-c['bb'][1]+1,'a',c['a'])
def fit(name, frames):
    d=tracks[name]; fr=[i for i in frames if i in d]
    t=np.array([cap(i) for i in fr],float); y=np.array([d[i]['c'][1] for i in fr])
    p=np.polyfit(t,y,2); r=y-np.polyval(p,t)
    print(name,'frames',fr,'a_px/capframe^2=%.2f'%(2*p[0]),'rms=%.2f'%r.std(),'-> Z(g=9.8,f=711)=%.2f m'%(9.8*711/625/(2*p[0])))
    return p
print()
fit('tennis',range(28,36)); fit('tennis',range(29,35)); fit('tennis',range(37,49))
fit('pineapple',range(30,36))
fit('soccer',range(31,40)); fit('soccer',range(40,49))
fit('box',range(34,39))
