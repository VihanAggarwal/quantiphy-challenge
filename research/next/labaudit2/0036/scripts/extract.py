import cv2, os, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
for v in ['captured_0036','captured_0036s','captured_0036x']:
    cap=cv2.VideoCapture(D+v+'.mp4')
    print(v, cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT), cap.get(3), cap.get(4))
    os.makedirs(f'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/{v}',exist_ok=True)
    k=0
    while True:
        ok,im=cap.read()
        if not ok: break
        cv2.imwrite(f'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/{v}/f{k:02d}.png',im); k+=1
    print(k)
