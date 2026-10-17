import numpy as np, cv2
from reg import *
cnt2=np.load(W+'rockcontour_0043_segmented_30.npy').astype(float)
def footprint(zs=1.0,**over):
    F=frame_of('C2',**over)
    # plane z=zs in boat frame -> in camera ENU: U = P1_U + zs
    h=-(F['P1'][2]+zs)
    G=F['cam'].ground(cnt2[:,0],cnt2[:,1],h)
    return to_boat(F,G)
if __name__=='__main__':
    for zs in [0,1,2]:
        Q=footprint(zs)
        print('zs',zs,'X range %.2f..%.2f (%.2f)  Y range %.2f..%.2f (%.2f)'%(Q[:,0].min(),Q[:,0].max(),np.ptp(Q[:,0]),Q[:,1].min(),Q[:,1].max(),np.ptp(Q[:,1])))
    Q=footprint(1.0)
    np.save(W+'c2_footprint_boatframe.npy',Q)
    # which contour points give extremes
    for nm,i in [('Xmin',Q[:,0].argmin()),('Xmax',Q[:,0].argmax()),('Ymin',Q[:,1].argmin()),('Ymax',Q[:,1].argmax())]:
        print(nm,np.round(Q[i],2),'img',cnt2[i])
