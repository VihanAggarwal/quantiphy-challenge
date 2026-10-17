from vio import *
import cv2
for v,k in [('0043_segmented',0),('0043_segmented',24),('0043_segmented',48),('0043_segmented',71),('0044',0),('0044',24),('0044',48),('0039',24),('0040',24),('0031',24)]:
    cv2.imwrite(W+'frames/%s_f%02d.png'%(v,k), frame(v,k))
