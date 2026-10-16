import cv2, os, sys
out='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
os.makedirs(out,exist_ok=True)
for v in ['a','as','ax','b','bs','bx']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0054{v}.mp4')
    i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/{v}_{i:02d}.png',f)
        i+=1
    print(v,i)
