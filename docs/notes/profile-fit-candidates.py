"""Adaptive circular arcs and cubic Bezier control-point spline alternatives."""
import json
import numpy as np
from scipy.integrate import quad
from profile_geometry import (ROOT, LENGTH, read_input, emit, save_json, add_metrics,
                              point_line_distance, uniform_indices, line_segments,
                              polygon_metrics, polyline_distances)


def arc_through(p):
    a, b, c = p[0], p[len(p)//2], p[-1]
    u, v = b-a, c-a
    center = a + np.linalg.solve(2*np.array([u, v]), np.array([u@u, v@v]))
    r = np.linalg.norm(a-center)
    angles = np.arctan2((p-center)[:, 1], (p-center)[:, 0])
    sweep = (angles[-1]-angles[0]) % (2*np.pi)
    if (angles[len(p)//2]-angles[0]) % (2*np.pi) > sweep:
        sweep -= 2*np.pi
    return dict(kind='arc', start=a.tolist(), end=c.tolist(), center=center.tolist(),
                radius=float(r), angle_start=float(angles[0]), sweep=float(sweep))


def arc_distances(p, seg):
    a, b, center = (np.array(seg[k]) for k in ('start', 'end', 'center'))
    angles = np.arctan2((p-center)[:, 1], (p-center)[:, 0])
    progress = ((angles-seg['angle_start'])*np.sign(seg['sweep'])) % (2*np.pi)
    radial = np.abs(np.linalg.norm(p-center, axis=1)-seg['radius'])
    endpoints = np.minimum(np.linalg.norm(p-a, axis=1), np.linalg.norm(p-b, axis=1))
    return np.where(progress <= abs(seg['sweep'])+1e-12, radial, endpoints)


def fit_arcs(p, tol, offset=0):
    if len(p) == 2:
        return [dict(kind='line', start=p[0].tolist(), end=p[-1].tolist(),
                     source_indices=[offset, offset+len(p)-1])]
    try:
        seg = arc_through(p)
        distances = arc_distances(p, seg)
        center = np.array(seg['center'])
        angles = np.unwrap(np.arctan2((p-center)[:, 1], (p-center)[:, 0]))
        monotone = np.all(np.diff(angles)*np.sign(seg['sweep']) >= -1e-10)
        if distances.max() <= tol and monotone:
            seg['source_indices'] = [offset, offset+len(p)-1]
            return [seg]
        split = int(distances.argmax()) if monotone else len(p)//2
    except np.linalg.LinAlgError:
        split = len(p)//2
    split = max(1, min(len(p)-2, split))
    return fit_arcs(p[:split+1], tol, offset) + fit_arcs(p[split:], tol, offset+split)


def arc_metrics_and_distances(segs, original):
    integrals = np.zeros(3)
    perimeter = 0.0
    extremes = []
    distances = np.full(len(original), np.inf)
    for seg in segs:
        a, b = np.array(seg['start']), np.array(seg['end'])
        extremes += [a.tolist(), b.tolist()]
        if seg['kind'] == 'line':
            def value(t):
                return a + t*(b-a), b-a
            distances = np.minimum(distances, point_line_distance(original, a, b))
            perimeter += np.linalg.norm(b-a)
        else:
            center = np.array(seg['center'])
            r, t0, sweep = (seg[k] for k in ('radius', 'angle_start', 'sweep'))
            def value(t):
                angle = t0 + sweep*t
                return center+r*np.array([np.cos(angle), np.sin(angle)]), r*sweep*np.array([-np.sin(angle), np.cos(angle)])
            distances = np.minimum(distances, arc_distances(original, seg))
            perimeter += r*abs(sweep)
            for theta in np.arange(4)*np.pi/2:
                if ((theta-t0)*np.sign(sweep)) % (2*np.pi) <= abs(sweep):
                    extremes.append((center+r*np.array([np.cos(theta), np.sin(theta)])).tolist())
        def integrand(t, j):
            (x, y), (dx, dy) = value(t)
            return [(x*dy-y*dx)/2, x*x*dy/2, -y*y*dx/2][j]
        integrals += [quad(integrand, 0, 1, args=(j,), epsabs=1e-10)[0] for j in range(3)]
    area = integrals[0]
    ext = np.array(extremes)
    metrics = dict(area_mm2=float(abs(area)), signed_area_mm2=float(area),
                   centroid_mm=(integrals[1:]/area).tolist(), bbox_min_mm=ext.min(0).tolist(),
                   bbox_max_mm=ext.max(0).tolist(), perimeter_mm=float(perimeter),
                   volume_mm3=float(abs(area)*LENGTH),
                   surface_area_mm2=float(2*abs(area)+LENGTH*perimeter))
    return metrics, distances


def fit_beziers(p, tol, offset=0):
    t = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    t /= t[-1]
    basis = np.array([(1-t)**3, 3*t*(1-t)**2, 3*t*t*(1-t), t**3]).T
    ends = basis[:, [0]]*p[0] + basis[:, [3]]*p[-1]
    interior = np.linalg.lstsq(basis[:, 1:3], p-ends, rcond=None)[0]
    controls = np.vstack((p[0], interior, p[-1]))
    residual = np.linalg.norm(basis@controls-p, axis=1)
    if residual.max() <= tol or len(p) <= 4:
        return [dict(kind='spline', points=controls.tolist(), source_indices=[offset, offset+len(p)-1])]
    split = max(2, min(len(p)-3, int(residual.argmax())))
    return fit_beziers(p[:split+1], tol, offset) + fit_beziers(p[split:], tol, offset+split)


def main():
    ps, ss = read_input()
    original = np.vstack((ps, ss[-2:0:-1]))
    manifest = json.loads((ROOT/'candidates.json').read_text())
    baseline = json.loads((ROOT/'baseline.json').read_text())
    for tol in (0.025, 0.01, 0.001):
        a, b = fit_arcs(ps, tol), fit_arcs(ss[::-1], tol)
        segs = a+b
        name = f'arcs_adaptive_{str(tol).replace(".", "p")}'
        emit(name, segs, comment=f'Adaptive 3-point circles, {tol} mm fit tolerance; {len(a)}/{len(b)} PS/SS pieces.')
        metrics, distances = arc_metrics_and_distances(segs, original)
        manifest[name] = dict(kind='arcs', segment_count=len(segs), segments_per_side=[len(a), len(b)],
                              segments=segs, metrics=add_metrics(metrics, distances, baseline))
        print(name, len(segs), manifest[name]['metrics'])
    for tol in (0.025, 0.01):
        a, b = fit_beziers(ps, tol), fit_beziers(ss[::-1], tol)
        name = f'spline_bezier_{str(tol).replace(".", "p")}'
        emit(name, a+b, experimental=True, comment=f'Endpoint-preserving least-squares cubic Bezier chunks, {tol} mm parameter-fit tolerance.')
        manifest[name] = dict(kind='spline_bezier', segment_count=len(a+b), segments_per_side=[len(a), len(b)],
                              controls_per_segment=4, segments=a+b)
        print(name, len(a+b))
    for n in (12, 24, 120, 240, 500, 1001):
        inds = uniform_indices(n)
        segs = [dict(kind='spline', points=ps[inds].tolist()), dict(kind='spline', points=ss[inds][::-1].tolist())]
        name = f'spline_raw_{n}'
        emit(name, segs, experimental=True, comment=f'{n} raw table points per side as spline controls.')
        manifest[name] = dict(kind='spline_raw', segment_count=2, point_count_per_side=n, segments=segs)
    # Few chunks of modest size: 4 x 8 controls on each side, common endpoints.
    for count in (8, 16):
        segs = []
        for side in (ps, ss[::-1]):
            for i in range(4):
                inds = np.round(np.linspace(i*250, (i+1)*250, count)).astype(int)
                segs.append(dict(kind='spline', points=side[inds].tolist()))
        name = f'spline_chunks_4x{count}'
        emit(name, segs, experimental=True, comment=f'Four raw-control chunks per side, {count} controls per chunk.')
        manifest[name] = dict(kind='spline_chunks', segment_count=8, segments_per_side=[4, 4],
                              controls_per_segment=count, segments=segs)
    # Coordinate-style comparisons and minimal experimental-flag probes.
    source=manifest['polyline_uniform_500']
    emit('polyline_literals_500',source['segments'],guesses=False,
         comment='500 table points per side, constant coordinates instead of var guesses.')
    manifest['polyline_literals_500']=dict(source,kind='polyline_literals')
    for source_name in ['polyline_adaptive_0p01','arcs_adaptive_0p001']:
        name=source_name+'_literals'
        source=manifest[source_name]
        emit(name,source['segments'],guesses=False,
             comment='Constant-coordinate version of '+source_name+'; solver-variable comparison.')
        manifest[name]=dict(source,kind=source['kind']+'_literals')
    segs=line_segments(original)
    name='polyline_literals_1001'
    emit(name,segs,guesses=False,
         comment='All 1001 source points on each side, 2000 straight edges; constant coordinates.')
    manifest[name]=dict(kind='polyline_literals',point_count_per_side=1001,segment_count=len(segs),segments=segs,
                        metrics=add_metrics(polygon_metrics(original),polyline_distances(original,original),baseline))
    inds=uniform_indices(4)
    segs=[dict(kind='spline',points=ps[inds].tolist()),dict(kind='spline',points=ss[inds][::-1].tolist())]
    for enabled in [False,True]:
        name='spline_raw_4' if enabled else 'spline_raw_4_no_flag'
        emit(name,segs,experimental=enabled,
             comment='Minimal cubic per side; syntax/experimental-flag probe, deliberately coarse fit.')
        manifest[name]=dict(kind='spline_raw',segment_count=2,point_count_per_side=4,segments=segs)
    save_json(ROOT/'candidates.json', manifest)


if __name__ == '__main__':
    main()
