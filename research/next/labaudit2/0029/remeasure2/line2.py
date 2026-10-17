import numpy as np,json
T=json.load(open('track_raw.json')); S=json.load(open('size_x2.json'))
def u(px,py,f=711.,cx=640.,cy=360.):
    v=np.array([(px-cx)/f,(py-cy)/f,1.]); return v/np.linalg.norm(v)
r=3.35
cap=lambda i:int(np.floor(i*25/24+0.5))
def pix(i,src):
    if src=='cent': return np.mean([[T[t][i][1],T[t][i][2]] for t in ['','s','x']],axis=0)
    if src=='circ': return np.array(S[str(i)]['all'][:2])
def run(src,f,ia,ra,ib,rb,rng):
    CA=(ra+r)*u(*pix(ia,src),f=f); CB=(rb+r)*u(*pix(ib,src),f=f)
    d=CB-CA; L=np.linalg.norm(d); dh=d/L; out=[]
    for i in rng:
        w=u(*pix(i,src),f=f)
        M=np.array([[1,-dh@w],[-dh@w,1]]); rhs=np.array([-(CA@dh),(CA@w)])
        s,t=np.linalg.solve(M,rhs); Cp=CA+s*dh; out.append((i,s,Cp,np.linalg.norm(Cp-t*w),w))
    return out,L
for src in ['cent','circ']:
    out,L=run(src,711,30,114.4,38,102.7,range(30,49))
    print(f'--- post-bounce line {src}: |C38-C30|={L:.2f}')
    for k,(i,s,Cp,miss,w) in enumerate(out):
        st=''
        if k+1<len(out):
            i2,s2,Cp2,_,w2=out[k+1]; dc=cap(i2)-cap(i)
            P1=(np.linalg.norm(Cp)-r)*w; P2=(np.linalg.norm(Cp2)-r)*w2
            st=f'dcap={dc} ctr {25*(s2-s)/dc:6.1f} cm/s surf {25*np.linalg.norm(P2-P1)/dc:6.1f} cm/s dR={np.linalg.norm(Cp2)-np.linalg.norm(Cp):5.2f}'
        print(f'v{i} c{cap(i)} s={s:6.2f} R={np.linalg.norm(Cp):6.1f} miss={miss:4.2f} {st}')
