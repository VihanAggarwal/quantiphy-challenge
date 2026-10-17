import cv2, sys, os
out='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/frames'
vid=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
w=cap.get(cv2.CAP_PROP_FRAME_WIDTH); h=cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(vid,n,fps,w,h)
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,img=cap.read()
    if ok: cv2.imwrite(f'{out}/{vid}_f{f:03d}.png',img)
