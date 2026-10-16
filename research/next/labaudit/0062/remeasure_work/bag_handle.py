import cv2, numpy as np
cx=640.;cy=360.;f=711.
n=np.load('n_fit_711.npy')[:3]
C=np.load('bag_corners_trim.npy')
def P(uv):
    uv=np.atleast_2d(uv).astype(float); r=np.c_[(uv[:,0]-cx)/f,(uv[:,1]-cy)/f,np.ones(len(uv))]; return r/(r@n)[:,None]
X=P(C)  # L,T,R,B
u_open=(X[2]-X[1]); u_open/=np.linalg.norm(u_open)   # TR direction
u_side=(X[1]-X[0]); u_side-= (u_side@u_open)*u_open; u_side/=np.linalg.norm(u_side)  # from bottom(BL) toward opening(TR)
m=cv2.imread('bag_mask.png',0)>0
ys,xs=np.nonzero(m); Q=P(np.c_[xs,ys])
# coordinates relative to L corner
a=(Q-X[0])@u_open; b=(Q-X[0])@u_side
print('mask extent along opening dir (h):',round(a.min(),4),round(a.max(),4),' along side dir:',round(b.min(),4),round(b.max(),4))
bodyB=((X-X[0])@u_side)
print('body side coords of corners',np.round(bodyB,4))
hb=1.8212
print('max extent from bottom edge to handle tip: %.1f cm ; body side %.1f cm ; handle protrusion %.1f cm'%((b.max()-0)*hb*100, (bodyB[1])*hb*100,(b.max()-bodyB[1])*hb*100))
print('body diagonal (h)', round(np.linalg.norm(X[2]-X[0]),4), round(np.linalg.norm(X[3]-X[1]),4),'-> cm',round(np.linalg.norm(X[2]-X[0])*hb*100,1),round(np.linalg.norm(X[3]-X[1])*hb*100,1))
# where is handle tip in image
k=np.argmax(b); print('handle tip px',xs[k],ys[k])
