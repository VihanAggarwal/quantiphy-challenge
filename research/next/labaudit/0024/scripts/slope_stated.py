import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
def bp(u,v,r): return ray(u,v)*r
# candidate click pairs (far=top edge, near=bottom edge)
for top,bot in [((804,361),(657,480)),((780,361),(640,476)),((830,361),(680,486)),((804,365),(657,476))]:
    d=np.linalg.norm(bp(*top,1.243)-bp(*bot,0.990))*100
    print(top,bot,'stated-depth slope length %.1f'%d)
# where on my slope model are ranges 1.243 / 0.990 reached?
for nm,X in dict(TL=TL,TR=TR,BL=BL,BR=BR).items(): print(nm,'%.3f'%np.linalg.norm(X))
print('top-mid range %.3f bottom-mid range %.3f'%(np.linalg.norm((TL+TR)/2),np.linalg.norm((BL+BR)/2)))
print('--- label emulation for click pairs with stated depths ---')
TLp=(751,360); TRp=(857,361); BLp=(609,467); BRp=(705,493)
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
for nm,(pf,pn) in {'TL-BL':(TLp,BLp),'TR-BR':(TRp,BRp),'TL-BR':(TLp,BRp),'topmid-botmid':(lerp(TLp,TRp,.5),lerp(BLp,BRp,.5)),
                   'TL-bot25':(TLp,lerp(BLp,BRp,.25)),'top25-bot25':(lerp(TLp,TRp,.25),lerp(BLp,BRp,.25))}.items():
    d=np.linalg.norm(bp(*pf,1.243)-bp(*pn,0.990))*100
    # also model ranges at those pixels
    Xf=on_slope(*pf); Xn=on_slope(*pn)
    print('%-14s stated-depth dist %.1f | model ranges far %.3f near %.3f | model dist %.1f'%(nm,d,np.linalg.norm(Xf),np.linalg.norm(Xn),np.linalg.norm(Xf-Xn)*100))
