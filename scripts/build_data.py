"""Ubah data/raw/*.xlsx menjadi data.js (dipakai index.html). Jalankan: python scripts/build_data.py"""
import pandas as pd, json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
Y = range(2021, 2026)
V = ['ipm','uhh','hls','rls','pengeluaran','miskin','tpt','tpak','gini','sanitasi','air_minum']
ISL = {1:'Sumatera',2:'Sumatera',3:'Jawa',5:'Bali–Nusa Tenggara',6:'Kalimantan',7:'Sulawesi',8:'Maluku',9:'Papua'}
def n(x):
    v = pd.to_numeric(x, errors='coerce')          # '-' (tidak tersedia) -> null
    return None if pd.isna(v) else round(float(v), 3)
s = lambda r, f: [n(r[f'{f} {y}']) for y in Y]
p = pd.read_excel(R/'data/raw/prov_panel.xlsx')
p = p.iloc[:, list(p.columns).index('kode'):]       # blok kedua = panel lengkap 38 provinsi
p.columns = [c.replace('.1', '') for c in p.columns]
k = pd.read_excel(R/'data/raw/kabkota_panel.xlsx')
P = [{'k':int(r.kode),'n':r.provinsi,'i':ISL[int(r.kode)//10],'v':{f:s(r,f) for f in V}} for _, r in p.iterrows()]
names = {x['n'] for x in P}
K = [{'k':int(r.kode),'n':r.kabkota,'p':r.provinsi,'i':ISL[int(r.kode)//1000],'ipm':s(r,'ipm tahun'),
      'mk':s(r,'miskin_persen'),'kp':s(r,'kepadatan'),'jm':s(r,'jml_miskin'),'ar':n(r.luas_km2),
      'lo':n(r.lon),'la':n(r.lat)} for _, r in k.iterrows()]
# KOREKSI: luas Kota Ambon di berkas mentah 35944.62 km2 (selisih 100x; luas resmi ±359.45 km2). Verifikasi ke BPS.
for d in K:
    if d['n']=='Kota Ambon' and d['ar']>10000: d['ar']=359.45
# KOREKSI KOORDINAT: lon/lat di berkas mentah salah/tertukar untuk entri berikut (mis. Sumedang jatuh di Kalimantan; banyak entri Papua tertukar).
# Nilai di bawah adalah perkiraan titik tengah kab/kota (±0,5°); ganti dengan centroid dari poligon batas BIG bila sudah ada.
FIX = {3211: (107.92, -6.86), 5107: (115.6, -8.4), 6211: (113.5, -1.3), 9101: (132.6, -3.0), 9102: (133.8, -3.7), 9103: (134.3, -2.8), 9104: (133.3, -2.2), 9105: (134.1, -0.9), 9111: (134.1, -1.5), 9112: (133.8, -1.3), 9107: (131.5, -1.0), 9106: (132.0, -1.5), 9110: (132.3, -1.4), 9109: (132.5, -0.7), 9403: (140.2, -2.6), 9408: (136.2, -1.8), 9409: (135.9, -1.0), 9419: (138.9, -2.5), 9420: (140.6, -3.3), 9426: (136.7, -2.5), 9427: (135.5, -0.8), 9428: (137.5, -2.5), 9471: (140.7, -2.55), 9401: (140.4, -8.4), 9413: (140.4, -6.1), 9414: (139.4, -7.1), 9415: (138.4, -5.5), 9412: (136.9, -4.6), 9434: (135.6, -4.0), 9436: (136.2, -4.1), 9404: (135.5, -3.4), 9410: (136.4, -3.9), 9435: (136.7, -3.6), 9433: (137.2, -4.0), 9411: (137.8, -3.6), 9508: (138.2, -4.5), 9402: (139.1, -4.0), 9430: (138.4, -4.0), 9418: (138.2, -3.65), 9705: (138.7, -3.4), 9432: (139.4, -3.6), 9416: (139.6, -4.7), 9417: (140.4, -4.7)}
for d in K:
    if d['k'] in FIX: d['lo'], d['la'] = FIX[d['k']]

# KOREKSI KOORDINAT (lebih akurat): centroid poligon BIG (kabkota_geojson.txt) dipakai bila kode kab/kota cocok; sisanya memakai FIX.
import re
G=json.load(open(R/'kabkota_geojson.txt'))
def cen(g):
    pgs=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
    pts=[p for pg in pgs for p in pg[0]]
    return sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)
GC={}
for f in G['features']:
    kk=f['properties']['KDPKAB']
    if not f['geometry'] or not kk or '/' in kk: continue
    GC[int(re.sub(r'\D','',kk))]=cen(f['geometry'])
nc=0
for d in K:
    if d['k'] in GC: d['lo'],d['la']=[round(v,3) for v in GC[d['k']]]; nc+=1
print(nc,'koordinat dari centroid poligon BIG')
assert all(d['p'] in names for d in K), 'nama provinsi tidak cocok'
(R/'data.js').write_text('window.D='+json.dumps({'P':P,'K':K}, ensure_ascii=False, separators=(',',':')), encoding='utf-8')
print(len(P), 'provinsi,', len(K), 'kab/kota')
