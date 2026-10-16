import cv2, os
out='/home/user/quantiphy-challenge/research/next/labaudit/0036/frames'
for v in ['captured_0036','captured_0036s','captured_0036x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    i=0
    os.makedirs(f'{out}/{v}',exist_ok=True)
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/{v}/f{i:02d}.png',f)
        i+=1
    print(v,i)
