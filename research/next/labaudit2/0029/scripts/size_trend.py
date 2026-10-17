# radial rate from the sub-pixel diameters: line fits pre-bounce (video 22-29) and post-bounce (video 31-48) on the capture clock
import numpy as np, json
S=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0029/sizefit.json'))
f=711.; Dball=0.067
cap=lambda k: k+(k>=12)+(k>=36)
for rend in ['o','s']:
    R={int(k):f*Dball/v[2] for k,v in S[rend].items()}
    for lo,hi in [(22,29),(23,29),(31,48),(31,40),(32,48)]:
        ks=[k for k in range(lo,hi+1) if k in R]; n=np.array([cap(k) for k in ks]); r=np.array([R[k] for k in ks])
        p=np.polyfit(n,r,1); res=r-np.polyval(p,n)
        print(rend,'video %d-%d: slope %+.2f cm/step  rms %.1f cm  line at n31 (video30) %.3f, n32 (video31) %.3f, n40 (video38) %.3f, n41 %.3f'%(lo,hi,100*p[0],100*res.std(),np.polyval(p,31),np.polyval(p,32),np.polyval(p,40),np.polyval(p,41)))
    print(rend,'measured centre range video 30: %.3f, 31: %.3f, 38: %.3f'%(R[30],R[31],R[38]),' stated+r: 1.178 (30), 1.061 (38)')
