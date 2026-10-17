import numpy as np
f=711.; cx,cy=640.,360.
down=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0054/m2_indep/down.npy')
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
r=0.116
# basketball centres (video frame -> capture): SAM-mask circle fit (A) and orange-threshold circle fit (B)
A={11:(312.2,597.3),12:(343.6,606.9),13:(360.7,613.1),24:(585.2,680.7)}
B={11:(312.3,590.3),12:(343.5,601.8),13:(359.7,606.0),24:(583.9,675.3)}
for name,C in (('SAMfit',A),('orangefit',B)):
    c11,c13,c14,c25=C[11],C[12],C[13],C[24]
    c12=((c11[0]+c13[0])/2,(c11[1]+c13[1])/2)
    s25=1.81+r
    k25=ray(*c25)@down
    for lab,c in (('c12',c12),('c13',c13),('c14',c14)):
        s=s25*k25/(ray(*c)@down)
        print(name,lab,'pixel',np.round(c,1),'predicted surface range %.3f (stated t=0.5: 2.3557) diff %.3f'%(s-r,s-r-2.3557))
