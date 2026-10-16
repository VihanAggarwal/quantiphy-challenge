import cv2, numpy as np
def fit_line(pts):
    pts = np.asarray(pts, np.float32)
    vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    n = np.array([-vy, vx]); c = -n @ np.array([x0, y0])
    return np.array([n[0], n[1], c])
def inter(a, b):
    p = np.cross(a, b); return p[:2] / p[2]
def quad_from_mask(mask, x0=0, y0=0, upsample=8, trim=0.2):
    """subpixel-ish: upsample the (soft) mask, find contour, approx 4 corners, refit sides."""
    m = cv2.resize(mask.astype(np.float32), None, fx=upsample, fy=upsample, interpolation=cv2.INTER_LINEAR)
    mb = (m > 0.5).astype(np.uint8)
    cs, _ = cv2.findContours(mb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(float)
    peri = cv2.arcLength(c.astype(np.float32), True)
    for eps in np.linspace(0.01, 0.1, 50):
        ap = cv2.approxPolyDP(c.astype(np.float32), eps * peri, True)
        if len(ap) == 4: break
    ap = ap[:, 0, :].astype(float)
    # assign contour points to sides
    lines = []
    for i in range(4):
        a, b = ap[i], ap[(i + 1) % 4]
        d = b - a; L = np.linalg.norm(d); u = d / L; n = np.array([-u[1], u[0]])
        rel = c - a; t = rel @ u; dist = np.abs(rel @ n)
        sel = (t > trim * L) & (t < (1 - trim) * L) & (dist < 3 * upsample)
        lines.append(fit_line(c[sel]))
    corners = np.array([inter(lines[i - 1], lines[i]) for i in range(4)])
    # convert from upsampled pixel-corner coordinates to original pixel-centre coordinates
    corners = (corners + 0.5) / upsample - 0.5 + np.array([x0, y0])
    return corners
