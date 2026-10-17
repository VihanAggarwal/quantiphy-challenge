import numpy as np, sys
sys.path.insert(0,'scripts')
from cam import *
B=np.load('dogbox.npy')
t=B[:,0]/24
for c0 in [3.68,3.73,3.78]:
    print('== c0',c0)
    for hz in [0.0,0.3,0.5]:
        ar=lambda r: np.sqrt(r*r-c0*c0-(h-hz)**2)
        print('  hz %.1f label a(0)=%.3f a(0.5)=%.3f  -> da=%.3f m in 0.5s (%.2f m/s)'%(hz,ar(5.094),ar(4.625),ar(5.094)-ar(4.625),(ar(5.094)-ar(4.625))/0.5))
    aL=a_from_u(B[:,1],c0); aR=a_from_u(B[:,2],c0); aC=a_from_u(B[:,5],c0); aM=a_from_u((B[:,1]+B[:,2])/2,c0)
    for i in [0,6,12,18,24,30,36,42,48]:
        print('   f%02d t=%.3f a_left(head)=%.3f a_right=%.3f a_centroid=%.3f a_bboxmid=%.3f'%(i,t[i],aL[i],aR[i],aC[i],aM[i]))
