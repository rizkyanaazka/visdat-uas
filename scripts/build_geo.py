"""Ubah batas wilayah kab/kota asli (shapefile / GeoJSON) menjadi geo.js untuk index.html.

Pakai (dari folder proyek):
    pip install geopandas
    python scripts/build_geo.py "[LapakGIS.com]_BATAS_KABKOTA_AR_EDISI_JULI_2026_.shp"
    python scripts/build_geo.py batas_sederhana.geojson --tol 0      # kalau sudah disederhanakan di mapshaper

Hasil: geo.js di folder proyek -> window.G = {kab: FeatureCollection, prov: FeatureCollection}
  kab : satu fitur per baris data.js (properti n = nama, p = provinsi, c = titik representatif [lon,lat])
  prov: satu fitur per provinsi (gabungan kab/kota), dipakai untuk garis pantai & batas provinsi

Pencocokan ke data.js memakai NAMA (provinsi + kab/kota), bukan kode, karena kode BIG (Kemendagri)
berbeda sistem dengan kode BPS di data.js.
"""
import argparse, json, pathlib, re, sys
import geopandas as gpd
import shapely
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

R = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument('src', help='berkas .shp atau .geojson/.json batas kab/kota')
ap.add_argument('--tol', type=float, default=0.01, help='toleransi penyederhanaan (derajat, 0.01 ~ 1 km); 0 = jangan sederhanakan')
ap.add_argument('--kab', default='WADMKK', help='kolom nama kab/kota (bawaan BIG: WADMKK)')
ap.add_argument('--prov', default='WADMPR', help='kolom nama provinsi (bawaan BIG: WADMPR)')
ap.add_argument('--out', default=str(R / 'geo.js'))
a = ap.parse_args()

D = json.loads((R / 'data.js').read_text('utf-8')[len('window.D='):])
K = D['K']


def key(s):
    s = (s or '').lower().replace('-', ' ')
    return re.sub(r'[^a-z0-9]', '', s)


# nama di berkas BIG -> nama di data.js (sama-sama sudah dinormalkan: huruf kecil tanpa spasi/tanda baca)
PROV_ALIAS = {'daerahistimewayogyakarta': 'diyogyakarta', 'daerahkhususibukotajakarta': 'dkijakarta'}
NAME_ALIAS = {
    'kotaadministrasijakartabarat': 'kotajakartabarat', 'kotaadministrasijakartapusat': 'kotajakartapusat',
    'kotaadministrasijakartaselatan': 'kotajakartaselatan', 'kotaadministrasijakartatimur': 'kotajakartatimur',
    'kotaadministrasijakartautara': 'kotajakartautara', 'administrasikepulauanseribu': 'kepulauanseribu',
    'kepsiautagulandangbiaro': 'siautagulandangbiaro', 'pasangkayu': 'mamujuutara', 'toba': 'tobasamosir',
}

g = gpd.read_file(a.src)
if g.crs is not None and g.crs.to_epsg() != 4326:
    g = g.to_crs(4326)
for c in (a.kab, a.prov):
    if c not in g.columns:
        sys.exit(f'Kolom "{c}" tidak ada. Kolom tersedia: {list(g.columns)}  (pakai --kab / --prov)')
n0 = len(g)
g = g[g[a.kab].fillna('').str.strip() != ''].copy()
print(f'{n0} baris dibaca; {n0 - len(g)} baris tanpa nama kab/kota dilewati (pulau kecil/area bermasalah).')
g['_p'] = g[a.prov].map(lambda s: PROV_ALIAS.get(key(s), key(s)))
g['_n'] = g[a.kab].map(lambda s: NAME_ALIAS.get(key(s), key(s)))
g['geometry'] = g.geometry.make_valid()

# gabungkan baris ganda (satu kab/kota terdiri dari beberapa bagian, mis. Konawe, Muna, Wakatobi)
by = {}
for _, r in g.iterrows():
    by.setdefault((r['_p'], r['_n']), []).append(r.geometry)
by_name = {}
for (p, n), v in by.items():
    by_name.setdefault(n, []).append((p, n))


def polys(geom):
    """ambil bagian poligon saja"""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == 'Polygon':
        return [geom]
    if geom.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return [q for x in geom.geoms for q in polys(x)]
    return []


geoms, miss, used = [], [], set()
for d in K:
    k = (key(d['p']), key(d['n']))
    if k not in by:                                   # cadangan: cocokkan hanya lewat nama bila unik
        c = [x for x in by_name.get(k[1], []) if x not in used]
        k = c[0] if len(c) == 1 else None
    if k is None:
        geoms.append(None); miss.append(f"{d['n']} ({d['p']})")
        continue
    used.add(k)
    geoms.append(unary_union(polys(unary_union(by[k]))))
print(f'cocok: {len(K) - len(miss)} dari {len(K)} kab/kota data.js')
extra = [k for k in by if k not in used]
if extra:
    print('baris berkas yang tidak terpakai (tidak ada di data.js):', extra)

# kab/kota yang tidak ada di berkas: bentuk cadangan = lingkaran seluas wilayah, dipotong dari tetangganya
approx = set()
if miss:
    print('TIDAK ADA di berkas batas -> dibuat bentuk perkiraan (ditandai a=1):', miss)
    for i, d in enumerate(K):
        if geoms[i] is not None:
            continue
        r = ((d['ar'] or 400) / 3.14159) ** .5 / 111
        circ = Point(d['lo'], d['la']).buffer(min(max(r, .05), .6), 16)
        nb = unary_union([geoms[j] for j, e in enumerate(K) if geoms[j] is not None and e['p'] == d['p']])
        geoms[i] = unary_union(polys(circ.difference(nb))) or circ
        approx.add(i)

# penyederhanaan dengan topologi terjaga (batas bersama tetap berimpit)
if a.tol > 0:
    try:
        arr = shapely.coverage_simplify(list(geoms), a.tol)
        geoms = list(arr)
        print(f'disederhanakan dengan coverage_simplify (tol={a.tol})')
    except Exception as e:
        print(f'coverage_simplify tidak tersedia/gagal ({type(e).__name__}); pakai simplify per fitur (batas bersama bisa sedikit bergeser).')
        print('  Saran: sederhanakan di mapshaper.org lalu jalankan dengan --tol 0')
        geoms = [x.simplify(a.tol, preserve_topology=True) for x in geoms]


def clean(geom, min_area=2e-6):
    out = []
    for q in polys(geom):
        if q.area < min_area:
            continue
        out.append(orient(q, 1.0))                    # luar berlawanan arah jarum jam, lubang searah
    return out


def rr(ring):
    pts, last = [], None
    for x, y in ring:
        p = (round(x, 3), round(y, 3))
        if p != last:
            pts.append(list(p)); last = p
    if pts and pts[0] != pts[-1]:
        pts.append(pts[0])
    return pts if len(pts) >= 4 else None


def coords(ps):
    out = []
    for q in ps:
        ex = rr(q.exterior.coords)
        if not ex:
            continue
        out.append([ex] + [h for h in (rr(i.coords) for i in q.interiors) if h])
    return out


def geojson(ps):
    c = coords(ps)
    return {'type': 'MultiPolygon', 'coordinates': c} if len(c) != 1 else {'type': 'Polygon', 'coordinates': c[0]}


kab, byp = [], {}
for i, d in enumerate(K):
    ps = clean(geoms[i])
    if not ps:
        continue
    big = max(ps, key=lambda q: q.area)
    rp = big.representative_point()                   # titik di dalam bagian terbesar (untuk lingkaran & titik awal)
    pr = {'n': d['n'], 'p': d['p'], 'c': [round(rp.x, 3), round(rp.y, 3)]}
    if i in approx:
        pr['a'] = 1
    kab.append({'type': 'Feature', 'properties': pr, 'geometry': geojson(ps)})
    byp.setdefault(d['p'], []).extend(ps)

# provinsi = gabungan kab/kota; lubang sangat kecil (celah antar poligon) ditambal
prov = []
for p, ps in byp.items():
    u = polys(unary_union([q.buffer(0) for q in ps]))
    fixed = [Polygon(q.exterior, [h for h in q.interiors if Polygon(h).area > 3e-4]) for q in u]
    fixed = clean(unary_union(fixed))
    prov.append({'type': 'Feature', 'properties': {'p': p}, 'geometry': geojson(fixed)})

G = {'kab': {'type': 'FeatureCollection', 'features': kab}, 'prov': {'type': 'FeatureCollection', 'features': prov}}
txt = 'window.G=' + json.dumps(G, ensure_ascii=False, separators=(',', ':')) + ';'
pathlib.Path(a.out).write_text(txt, encoding='utf-8')
npt = sum(len(r) for f in kab for pg in ([f['geometry']['coordinates']] if f['geometry']['type'] == 'Polygon' else f['geometry']['coordinates']) for r in pg)
print(f'{len(kab)} kab/kota, {len(prov)} provinsi, {npt} titik -> {a.out} ({len(txt) / 1e6:.2f} MB)')
if len(txt) > 6e6:
    print('Ukuran besar; naikkan --tol (mis. 0.02) agar halaman tetap ringan.')
