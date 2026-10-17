import numpy as np, json, sys
src=open('planar.py').read().split('results=[]')[0]
CX=float(sys.argv[1]); CY=float(sys.argv[2])
src=src.replace('f=711.;cx=640.;cy=360.',f'f=711.;cx={CX};cy={CY}')
sys.argv=[sys.argv[0],'4,22,34,47']
exec(src)
out=[]
for pitch in [33,37,41]:
    for roll in [-2,2,6,10,14]:
        n=nvec(pitch,roll); tot=0;cnt=0
        for j in pairs:
            c,psi,phi=fitpair(n,j); tot+=c; cnt+=len(data[j][0])
        out.append((tot/cnt,pitch,roll))
out.sort()
print(CX,CY,'best',[(round(a,3),b,c) for a,b,c in out[:4]],' r(37,2)=',[round(a,3) for a,b,c in out if b==37 and c==2])
