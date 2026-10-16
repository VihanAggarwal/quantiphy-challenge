import cv2, numpy as np, sys
f=711.;cx=640.;cy=360.
K=np.array([[f,0,cx],[0,f,cy],[0,0,1]])
n=np.load('n_fit_711.npy')[:3]
def plane_basis(n):
    # e1 along corridor-ish: project camera z onto plane
    z=np.array([0,0,1.]); e2=z-(z@n)*n; e2/=np.linalg.norm(e2); e1=np.cross(n,e2); e1/=np.linalg.norm(e1)
    return e1,e2
def topview(img,h,center_px,half_cm=60,ppc=5):
    e1,e2=plane_basis(n)
    r=np.array([(center_px[0]-cx)/f,(center_px[1]-cy)/f,1.]); X0=h*r/(n@r)
    N=int(2*half_cm*ppc)
    a=(np.arange(N)-N/2)/ppc/100.
    A,B=np.meshgrid(a,-a)  # B up = far
    P=X0[None,None,:]+A[...,None]*e1+B[...,None]*e2
    u=f*P[...,0]/P[...,2]+cx; v=f*P[...,1]/P[...,2]+cy
    return cv2.remap(img,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR)
if __name__=='__main__':
    h=1.85
    img=cv2.imread('frames/o_00.png'); tv=topview(img,h,(830,335),half_cm=50,ppc=6); cv2.imwrite('top_bag_o00.png',tv)
    img=cv2.imread('frames/o_05.png'); tv=topview(img,h,(980,640),half_cm=70,ppc=5); cv2.imwrite('top_board_o05.png',tv)
    img=cv2.imread('frames/o_44.png'); tv=topview(img,h,(580,310),half_cm=70,ppc=5); cv2.imwrite('top_board_o44.png',tv)
