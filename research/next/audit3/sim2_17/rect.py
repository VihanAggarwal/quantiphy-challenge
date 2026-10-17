import cv2,numpy as np
def rect(im,S=4,th=25.64,u0=-700,u1=600,d0=85,d1=160):
    M=cv2.getRotationMatrix2D((960,540),-th,1.0)
    # after M, VP at (960,540); want output coords X=(u-u0)*S, Y=(d-d0)*S
    M[:,2]+= [-(960+u0), -(540+d0)]
    M2=M*S
    return cv2.warpAffine(im,M2,(int((u1-u0)*S),int((d1-d0)*S)),flags=cv2.INTER_CUBIC)
