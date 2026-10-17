import cv2,sys
v=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
scale=float(sys.argv[3]) if len(sys.argv)>3 else 1.0
c=cv2.VideoCapture(f"/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4")
for f in frames:
    c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read()
    if not ok: print("fail",f); continue
    if scale!=1: im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"crops/{v}_f{f}.jpg",im,[cv2.IMWRITE_JPEG_QUALITY,85])
