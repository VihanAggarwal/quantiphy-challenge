import cv2, numpy as np, json, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work')
from recon import *
f=float(sys.argv[1]) if len(sys.argv)>1 else 4240.
K,Ki,D,L,U=cam(f)
TL=json.load(open(W+'taillights.json'))
QL,_=tri({int(k):v for k,v in TL['TLL'].items() if int(k)>=22},f)
QR,_=tri({int(k):v for k,v in TL['TLR'].items() if int(k)>=31},f)
O=(QL+QR)/2
print('TL mid height below camera (V-units):',-(O@U))
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(cv2.resize(im,(1280,720),interpolation=cv2.INTER_AREA).astype(np.float32))
bg=cv2.resize(cv2.imread(W+'bg.png'),(1280,720),interpolation=cv2.INTER_AREA).astype(np.float32)
S=np.diag([0.5,0.5,1.0])
Kh=S@K
def masks(k):
    im=fr[k]
    ratio=(im.sum(2)+1)/(bg.sum(2)+1)
    diff=np.abs(im-bg).max(2)
    r,g,b=im[...,2],im[...,1],im[...,0]
    car=((r-g)>25)|(diff>40)&(ratio>0.85)
    car=cv2.dilate(car.astype(np.uint8),np.ones((7,7),np.uint8))>0
    sh=(ratio<0.72)&(~car)
    sh=cv2.morphologyEx(sh.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
    # restrict to neighbourhood of car (shadow near car)
    return sh,car
kr=48
shr,carr=masks(kr)
def score(hc,ks):
    tot=0;n=0
    for k in ks:
        sh,car=masks(k) if k not in cache else cache[k]
        t=(kr-k)/24.0*D
        Hm=Kh@(np.eye(3)-np.outer(t,U)/hc)@np.linalg.inv(Kh)
        w=cv2.warpPerspective(sh.astype(np.uint8),Hm,(1280,720),flags=cv2.INTER_NEAREST)>0
        wc=cv2.warpPerspective(car.astype(np.uint8),Hm,(1280,720),flags=cv2.INTER_NEAREST)>0
        valid=~(carr|wc)
        # region near car shadow: bbox around reference shadow union
        a=w&valid; b=shr&valid
        inter=(a&b).sum(); uni=(a|b).sum()
        tot+=inter/max(uni,1); n+=1
    return tot/n
cache={}
ks=[30,36,40,44,52,56,60,66]
for k in ks: cache[k]=masks(k)
cv2.imwrite(W+'shadowmask48.png',(np.dstack([shr*255,carr*255,shr*0]).astype(np.uint8)))
best=None
for hc in np.linspace(1.66,1.84,37):
    s=score(hc,ks); print('hc %.3f iou %.4f  ground rel TL %.4f'%(hc,s,-hc-(O@U)))
