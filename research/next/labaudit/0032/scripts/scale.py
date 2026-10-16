import numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
G=np.load(d+'plane711.npy',allow_pickle=True).item()
n=-G['n']  # pointing down (+y)
f=711.; K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); Ki=np.linalg.inv(K)
C=json.load(open(d+'corners.json'))
T=json.load(open(d+'track_x.json'))
def ray(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
# table unit points with n.X = 1
U={k: ray(v)/(n@ray(v)) for k,v in C.items()}
Wu=(np.linalg.norm(U['BR']-U['BL'])+np.linalg.norm(U['FR']-U['FL']))/2
Du=(np.linalg.norm(U['FL']-U['BL'])+np.linalg.norm(U['FR']-U['BR']))/2
print('unit W',Wu,'D',Du)
for name,key,R,rad in [('tennis','yel',1.183,0.0335),('pingpong','wht',1.353,0.02)]:
    t=T['36'][key]
    for lab,p in [('centroid',(t['cx'],t['cy'])),('bbox',t['bbc'])]:
        u=ray(p); X=R*u; h=n@X+rad
        print(name,lab,p,'cam height above top from stated range: %.4f m'%h,' -> W=%.1f cm D=%.1f cm'%(100*h*Wu,100*h*Du))
