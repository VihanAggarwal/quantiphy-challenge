from vio import *
import cv2
for v,k in [('0024_segmented',0),('0024_segmented',24),('0024_segmented',48),('0024_segmented',74),('0028_segmented',24),('0028_segmented',48)]:
    cv2.imwrite(W+'frames/%s_f%02d.png'%(v,k), frame(v,k))
