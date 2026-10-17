import numpy as np,json
T=json.load(open('track_raw.json')); S=json.load(open('size_x2.json'))
def u(px,py,f=711.,cx=640.,cy=360.):
    v=np.array([(px-cx)/f,(py-cy)/f,1.]); return v/np.linalg.norm(v)
r=3.35
def pix(i,src):
    if src=='cent': return np.mean([[T[t][i][1],T[t][i][2]] for t in ['','s','x']],axis=0)
    if src=='circ': return np.array(S[str(i)]['all'][:2])
for src in ['cent','circ']:
  for f in [711,690,730]:
    C24=(90.1+r)*u(*pix(24,src),f=f); C30=(114.4+r)*u(*pix(30,src),f=f)
    d=C30-C24; L=np.linalg.norm(d); dh=d/L
    out=[]
    for i in range(20,31):
        w=u(*pix(i,src),f=f)
        # closest points between line C24+s*dh and ray t*w
        A=np.array([[1,-dh@w],[dh@w,-1]]); b=np.array([-(C24@dh)+0, -(C24@w)])
        # solve for s,t minimizing |C24+s dh - t w|
        M=np.array([[dh@dh,-dh@w],[-dh@w,w@w]]); rhs=np.array([-(C24@dh),(C24@w)])
        s,t=np.linalg.solve(M,rhs); Cp=C24+s*dh; miss=np.linalg.norm(Cp-t*w)
        out.append((i,s,Cp,t,miss))
    print(f'--- {src} f={f}  line length {L:.2f} cm')
    for k,(i,s,Cp,t,miss) in enumerate(out):
        st=''
        if k+1<len(out):
            i2,s2,Cp2,t2,_=out[k+1]
            # label-style surface points: P=(|C|-r)*u
            P1=(np.linalg.norm(Cp)-r)*u(*pix(i,src),f=f); P2=(np.linalg.norm(Cp2)-r)*u(*pix(i2,src),f=f)
            st=f'ctr step {s2-s:5.2f} cm -> {25*(s2-s):6.1f} cm/s ; surf step {np.linalg.norm(P2-P1):5.2f} -> {25*np.linalg.norm(P2-P1):6.1f} cm/s ; dRange {np.linalg.norm(Cp2)-np.linalg.norm(Cp):5.2f}'
        print(f'v{i} s={s:6.2f} range_ctr={np.linalg.norm(Cp):6.1f} miss={miss:4.2f}  {st}')
