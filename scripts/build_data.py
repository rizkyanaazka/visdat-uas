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
assert all(d['p'] in names for d in K), 'nama provinsi tidak cocok'
(R/'data.js').write_text('window.D='+json.dumps({'P':P,'K':K}, ensure_ascii=False, separators=(',',':')), encoding='utf-8')
print(len(P), 'provinsi,', len(K), 'kab/kota')
