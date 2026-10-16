import numpy as np, json
cx=640.; f=711.; cy=360.
C=json.load(open('board_corners_o.json'))
Cs=np.load('static_corners.npy')
def bp(Q,n):
    r=np.c_[(Q[:,0]-cx)/f,(Q[:,1]-cy)/f,np.ones(len(Q))]; return r/(r@n)[:,None]
def centre(Q):
    p=[np.r_[q,1] for q in Q]; c=np.cross(np.cross(p[0],p[2]),np.cross(p[1],p[3])); return c[:2]/c[2]
for name in ['n_fit_711','n_cc','n_seams']:
    n=np.load(name+'.npy')[:3]
    Ls=[];Ws=[]
    for k,Q in C.items():
        if int(k)<20: continue
        X=bp(np.array(Q),n); s=[np.linalg.norm(X[(j+1)%4]-X[j]) for j in range(4)]
        Ls.append((s[0]+s[2])/2); Ws.append((s[1]+s[3])/2)
    X=bp(Cs,n); ss=[np.linalg.norm(X[(j+1)%4]-X[j]) for j in range(4)]
    # h from board range 2.815 at frame 33.6
    rr=[]
    for k in ['33','34']:
        c=centre(np.array(C[k])); X=bp(c[None],n)[0]; rr.append(np.linalg.norm(X))
    r336=rr[0]+0.6*(rr[1]-rr[0]); hb=2.815/r336
    # bag
    d=np.array([(837.5-cx)/f,(329.2-cy)/f,1]); d/=np.linalg.norm(d); hbag=3.307*(n@d)+0.01
    print(name,'L/h med',round(np.median(Ls),4),'sd',round(np.std(Ls),4),'W/h med',round(np.median(Ws),4),'sd',round(np.std(Ws),4),'static far/near',round(ss[0],4),round(ss[2],4),'left/right',round(ss[3],4),round(ss[1],4))
    print('   h_board',round(hb,4),'-> L',round(np.median(Ls)*hb*100,1),'W',round(np.median(Ws)*hb*100,1),' | h_bag',round(hbag,4),'-> L',round(np.median(Ls)*hbag*100,1),'W',round(np.median(Ws)*hbag*100,1))
