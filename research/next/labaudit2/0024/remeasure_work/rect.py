import numpy as np
f=711.;cx=640;cy=360
def K1(u,v): return np.array([(u-cx)/f,(v-cy)/f,1.])
def rect(FL,FR,BR,BL,verbose=True):
    # solve a*FL' + c*BR' = b*FR' + d*BL' with a=1 (parallelogram: FL+BR = FR+BL)
    r=[K1(*p) for p in (FL,FR,BR,BL)]
    A=np.stack([-r[1],r[2],-r[3]],1)  # unknowns b,c,d : c*BR - b*FR - d*BL = -FL
    b,c,d=np.linalg.lstsq(A,-r[0],rcond=None)[0]
    P=[r[0],b*r[1],c*r[2],d*r[3]]
    e1=P[1]-P[0]; e2=P[3]-P[0]
    cosang=e1@e2/np.linalg.norm(e1)/np.linalg.norm(e2)
    n=np.cross(e1,e2);n/=np.linalg.norm(n)
    ratio=np.linalg.norm(e2)/np.linalg.norm(e1)
    if verbose: print('depth ratios',np.round([1,b,c,d],3),'angle %.1f deg'%np.degrees(np.arccos(cosang)),'side(FL-BL)/front(FL-FR)=%.3f'%ratio,'normal',np.round(n,3))
    return ratio,P
if __name__=='__main__':
    rect((720.8,379.2),(808.3,385),(843.3,352.5),(756.7,351.7))
