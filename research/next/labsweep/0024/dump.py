import cv2, sys
v, idxs, scale = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], float(sys.argv[3]) if len(sys.argv)>3 else 0.5
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
i = 0
while True:
    ok, f = c.read()
    if not ok: break
    if i in idxs:
        g = cv2.resize(f, None, fx=scale, fy=scale)
        cv2.putText(g, f'{v} f{i}', (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        cv2.imwrite(f'png_{v}_{i}.png', g)
    i += 1
