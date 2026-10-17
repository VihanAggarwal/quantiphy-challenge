import numpy as np, cv2
L=(-0.3652826579939701,612.0073156202361); B=(0.04632883632605227,425.40407014831453)
R=(0.5312456515914249,-19.56659455713164); F=(0.05523306496781389,523.7551456029487)
def X(a,b):
    x=(b[1]-a[1])/(a[0]-b[0]); return np.array([x,a[0]*x+a[1]])
FL,FR,BR,BL=X(L,F),X(R,F),X(R,B),X(L,B)
print('FL',FL,'FR',FR,'BR',BR,'BL',BL)
img=np.array([FL,FR,BR,BL],float)
sq=np.array([[0,0],[1,0],[1,1],[0,1]],float)
H,_=cv2.findHomography(sq,img)
def analyze(f,cx=640,cy=360):
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
    M=np.linalg.inv(K)@H
    h1,h2=M[:,0],M[:,1]
    cos=h1@h2/np.linalg.norm(h1)/np.linalg.norm(h2)
    return cos,np.linalg.norm(h1)/np.linalg.norm(h2)
for f in [600,650,700,711,750,800,900]:
    print(f,analyze(f))
# solve f for orthogonality
from scipy.optimize import brentq
fo=brentq(lambda f: analyze(f)[0],300,3000)
print('f_orth',fo,analyze(fo))
