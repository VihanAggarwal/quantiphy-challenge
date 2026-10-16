import numpy as np, cv2
from plane import C
# table rectangle: FL(0,0) FR(60.3,0) BR(60.3,76) BL(0,76)  [cm], x along front edge, y receding
src=np.float32([C['FL'],C['FR'],C['BR'],C['BL']])
dst=np.float32([[0,0],[60.3,0],[60.3,76.0],[0,76.0]])
H=cv2.getPerspectiveTransform(src,dst)
def T(p):
    q=H@np.array([p[0],p[1],1.0]); return q[:2]/q[2]
def L(a,b): return np.linalg.norm(T(a)-T(b))
if __name__=='__main__':
    books={'s':[(625.5,388.3),(663.7,383.9),(681.9,425.5),(640.4,431.9)],
           'x':[(626,389.75),(662.5,384),(681.9,423.1),(640.6,431.9)]}
    for k,(FLb,FRb,NRb,NLb) in books.items():
        print(k,'far',round(L(FLb,FRb),2),'near',round(L(NLb,NRb),2),'left',round(L(FLb,NLb),2),'right',round(L(FRb,NRb),2))
    print('pen',round(L((434.4,440.0),(501.5,433.5)),2))
    TL=(500,314);TR=(593,304);BR=(609,407);BL=(509,422)
    print('board bottom edge width (on table)',round(L(BL,BR),2))
