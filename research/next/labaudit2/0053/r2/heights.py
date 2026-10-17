import numpy as np
f=711.;cx=640.;cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
N=np.load('normals.npy')
ball=ray(985.9,369.6)*(2.925+0.116)
book=ray(665,614)*2.082
cup=ray(565,425)*2.516
for n,name in zip(N,['horizon','vertVP']):
    print(name,'n.ball',n@ball,'n.book',n@book,'n.cup',n@cup)
    # camera height from ball (centre at 0.116)
    H=0.116-n@ball
    print('  cam height from ball',H,' book top height',n@book+H,' cup click height',n@cup+H)
