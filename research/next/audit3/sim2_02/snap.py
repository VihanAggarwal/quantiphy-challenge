import cv2, sys
v, f = sys.argv[1], int(sys.argv[2])
scale = float(sys.argv[3]) if len(sys.argv)>3 else 0.5
crop = sys.argv[4] if len(sys.argv)>4 else None
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES, f); ok, im = c.read()
if crop:
    x0,y0,x1,y1 = map(int, crop.split(','))
    im = im[y0:y1, x0:x1]
im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_NEAREST)
out = f'snap_{v}_{f}' + ('_c' if crop else '') + '.png'
cv2.imwrite(out, im); print(out, im.shape)
