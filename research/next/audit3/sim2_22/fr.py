import cv2, sys
def frame(v, i):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
    c.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, f = c.read()
    return f
def frames(v):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4')
    out = []
    while True:
        ok, f = c.read()
        if not ok: break
        out.append(f)
    return out
def save(name, img, scale=1.0, grid=None):
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    img = img.copy()
    if grid:
        h, w = img.shape[:2]
        step = grid
        for x in range(0, w, int(step*scale) if scale!=1 else step):
            cv2.line(img, (x,0), (x,h), (0,255,255), 1)
            cv2.putText(img, str(int(x/scale)), (x+2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,255), 1)
        for y in range(0, h, int(step*scale) if scale!=1 else step):
            cv2.line(img, (0,y), (w,y), (0,255,255), 1)
            cv2.putText(img, str(int(y/scale)), (2, y+12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,255), 1)
    cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_22/png/{name}.png', img)
