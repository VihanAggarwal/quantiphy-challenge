import numpy as np, json
cx=640.; cy=360.
v=np.load('n_fit_711.npy'); n=v[:3]; f=v[5]
C=json.load(open('board_corners_o.json'))
def bp(Q):
    r=np.c_[(Q[:,0]-cx)/f,(Q[:,1]-cy)/f,np.ones(len(Q))]; return r/(r@n)[:,None]
X={int(k):bp(np.array(Q)) for k,Q in C.items() if int(k)>=20}
for k in [22,27,33,34,40,46]:
    a=X[k]; b=X[k+1] if k+1 in X else X[k+2]
    m=b.mean(0)-a.mean(0); m/=np.linalg.norm(m)
    long=a[1]-a[0]; long/=np.linalg.norm(long); short=a[3]-a[0]; short/=np.linalg.norm(short)
    print(k,'cos(motion,long)',round(abs(m@long),3),'cos(motion,short)',round(abs(m@short),3))
