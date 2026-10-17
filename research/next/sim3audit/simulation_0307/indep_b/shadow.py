import numpy as np
from sweep import sweep, E, C
SP={'S_Ltip':(818,1147),'S_Rtip':(1552,1010),'S_spikeL':(935,1032),'S_spikeR':(1262,963),'S_LpodTail':(1105,1185),'S_RpodTail':(1450,1103),
    'S_triTipR':(1478,1186),'S_triBL':(1262,1228),'S_notch':(1330,1165),'S_holeLL':(955,1098),'S_holeLR':(1040,1093),'S_holeRL':(1270,1028),'S_holeRR':(1350,1020),
    'S_TEmid':(1150,1140)}
qs=np.linspace(0.0090,0.0160,281)
res={}
for k,p in SP.items():
    out=[]
    for r in [10,16]:
        q,c,_=sweep('0305',p,r=r,qs=qs,ref=24,fr=list(range(26,72,2)))
        out.append((q,c))
    res[k]=out
    print(k,p,' '.join('q=%.6f c=%.3f'%o for o in out))
np.save('shadow_q.npy',{k:(SP[k],v) for k,v in res.items()},allow_pickle=True)
