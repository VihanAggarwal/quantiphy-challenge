"""Re-measure the freestanding art display panel (qid 1657 width, 1089/1658 height).
Upright frame convention: original clip rotated CCW; segmented clip is stored upright.
Horizon / principal point at (540,540) (receding floor seams meet there; agent notes).
"""
import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0017_segmented.mp4')
cap.set(1,0); ok,b=cap.read()
fg=(np.abs(b.astype(int)-255).sum(2)>60)
def runs(r):
    idx=np.nonzero(r)[0]; out=[]
    if len(idx)==0: return out
    s=p=idx[0]
    for x in idx[1:]:
        if x!=p+1: out.append((s,p)); s=x
        p=x
    out.append((s,p)); return out
# right panel (not occluded by the pedestal): x>=660
top=min(y for y in range(440,620) if any(a>=660 and b2<=800 and b2-a>20 for a,b2 in runs(fg[y])))
base_rows=range(603,610)
wid=[max(b2 for a,b2 in runs(fg[y]) if 660<=a and b2<=800)-min(a for a,b2 in runs(fg[y]) if 660<=a and b2<=800)+1 for y in base_rows]
print('right panel top row',top,'base widths rows 603-609',wid)
frame_w=[max(b2 for a,b2 in runs(fg[y]) if 660<=a and b2<=800)-min(a for a,b2 in runs(fg[y]) if 660<=a and b2<=800)+1 for y in range(520,590,10)]
print('frame widths',frame_w)
px_w=118.0   # base X-extent, read on gridded zoom of original frame (664..783)
y_top=464.5; y_bot=(610.5+614.5)/2  # base bottom edge slants 610.5 (left) -> 614.5 (right)
v=y_bot-540
for name,Hc in [('static depth_info Z (agent)',0.964),('person planted foot (agent)',0.970),('floor seams + 0016 tile 1.323 m',0.974)]:
    W=Hc*px_w/v; Z=Hc*888/v
    Hgt=Hc+(540-y_top)*Z/888
    print(f'{name:35s} Hc={Hc:.3f} Z_front={Z:5.2f}  width={W:.3f}  height={Hgt:.3f}')
print('family-ratio route: 1.98 *', px_w, '/', y_bot-y_top, '=', round(1.98*px_w/(y_bot-y_top),3))
print('implied Z if 0.37 were right (px 92 frame):', round(0.37*888/92,2),' person Z at frame 40 ~4.7 m occludes panel -> impossible for Euclid 4.223')
