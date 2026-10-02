"""Membuat DATA DUMMY untuk prototipe. BUKAN data BPS.

Semua angka, kode wilayah, dan poligon di sini karangan acak. Hapus file ini dan
isi folder data/ dengan hasil preprocess.py (data BPS asli) saat data sudah ada.
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(2026)
TAHUN = [2021, 2022, 2023, 2024, 2025]

# nama, pulau, jumlah kab/kota (perkiraan kasar), pusat (lon, lat), skor latar (-1.5..1.5)
P = [
    ("Aceh", "Sumatera", 23, (96.8, 4.5), -0.2),
    ("Sumatera Utara", "Sumatera", 33, (99.0, 2.5), 0.2),
    ("Sumatera Barat", "Sumatera", 19, (100.5, -0.9), 0.4),
    ("Riau", "Sumatera", 12, (101.8, 0.5), 0.4),
    ("Jambi", "Sumatera", 11, (102.5, -1.6), 0.1),
    ("Sumatera Selatan", "Sumatera", 17, (104.0, -3.2), 0.0),
    ("Bengkulu", "Sumatera", 10, (102.3, -3.8), 0.0),
    ("Lampung", "Sumatera", 15, (105.2, -4.9), -0.1),
    ("Kepulauan Bangka Belitung", "Sumatera", 7, (106.3, -2.2), 0.3),
    ("Kepulauan Riau", "Sumatera", 7, (104.9, 0.9), 0.9),
    ("DKI Jakarta", "Jawa", 6, (106.8, -6.2), 1.5),
    ("Banten", "Jawa", 8, (105.6, -6.5), 0.5),
    ("Jawa Barat", "Jawa", 27, (108.2, -7.1), 0.4),
    ("Jawa Tengah", "Jawa", 35, (110.9, -7.4), 0.0),
    ("DI Yogyakarta", "Jawa", 5, (110.4, -8.9), 1.1),
    ("Jawa Timur", "Jawa", 38, (113.3, -8.0), 0.3),
    ("Bali", "Bali dan Nusa Tenggara", 9, (115.4, -8.5), 1.0),
    ("Nusa Tenggara Barat", "Bali dan Nusa Tenggara", 10, (117.2, -8.6), -0.5),
    ("Nusa Tenggara Timur", "Bali dan Nusa Tenggara", 22, (121.5, -9.5), -1.1),
    ("Kalimantan Barat", "Kalimantan", 14, (110.8, -0.2), -0.4),
    ("Kalimantan Tengah", "Kalimantan", 14, (113.5, -1.7), 0.0),
    ("Kalimantan Selatan", "Kalimantan", 13, (115.2, -3.0), 0.3),
    ("Kalimantan Timur", "Kalimantan", 10, (116.6, 0.3), 1.0),
    ("Kalimantan Utara", "Kalimantan", 5, (116.8, 3.0), 0.0),
    ("Sulawesi Utara", "Sulawesi", 15, (124.8, 1.0), 0.5),
    ("Gorontalo", "Sulawesi", 6, (122.4, 0.6), -0.3),
    ("Sulawesi Tengah", "Sulawesi", 13, (121.0, -1.0), -0.3),
    ("Sulawesi Barat", "Sulawesi", 6, (119.4, -2.6), -0.7),
    ("Sulawesi Selatan", "Sulawesi", 24, (120.0, -4.3), 0.3),
    ("Sulawesi Tenggara", "Sulawesi", 17, (122.2, -4.0), 0.0),
    ("Maluku", "Maluku", 11, (128.0, -3.4), -0.4),
    ("Maluku Utara", "Maluku", 10, (127.8, 1.2), -0.2),
    ("Papua Barat", "Papua", 7, (132.5, -1.5), -0.6),
    ("Papua Barat Daya", "Papua", 6, (131.0, -0.9), -0.7),
    ("Papua Selatan", "Papua", 4, (139.5, -7.0), -1.3),
    ("Papua", "Papua", 9, (139.0, -3.0), -1.2),
    ("Papua Tengah", "Papua", 8, (136.0, -4.0), -1.4),
    ("Papua Pegunungan", "Papua", 8, (138.5, -4.6), -1.5),
]

# ---------- referensi provinsi (kode DUMMY berurutan) ----------
ref = pd.DataFrame(
    [(str(11 + i), n, pulau, "") for i, (n, pulau, *_ ) in enumerate(P)],
    columns=["kode", "provinsi", "pulau", "alias"],
)
ref.to_csv(OUT / "ref_provinsi.csv", index=False)

# ---------- panel provinsi ----------
rows = []
for i, (nama, pulau, _, _, d) in enumerate(P):
    kode = str(11 + i)
    for t in TAHUN:
        k = t - 2021
        n = lambda s: rng.normal(0, s)
        rows.append(dict(
            kode=kode, provinsi=nama, pulau=pulau, tahun=t,
            ipm=72.5 + 4.0 * d + 0.8 * k + n(0.4),
            uhh=70.0 + 2.5 * d + 0.2 * k + n(0.3),
            hls=12.8 + 1.0 * d + 0.05 * k + n(0.15),
            rls=8.6 + 1.1 * d + 0.1 * k + n(0.15),
            pengeluaran=11500 + 2500 * d + 300 * k + n(350),
            miskin=max(2.5, 9.5 - 3.5 * d - 0.3 * k + n(0.6)),
            tpt=max(1.5, 5.0 - 0.5 * d - 0.2 * k + n(0.9)),
            tpak=68.0 + 1.0 * d + n(2.5),
            gini=0.37 + 0.02 * d + n(0.012),
            sanitasi=min(99, 82 + 10 * d + 1.2 * k + n(2)),
            air_minum=min(99.5, 90 + 7 * d + 0.8 * k + n(1.5)),
        ))
prov = pd.DataFrame(rows).round(3)
prov.to_csv(OUT / "provinsi_panel.csv", index=False)

# ---------- kab/kota + GeoJSON grid ----------
CELL = 0.3
feats, krows, boxes = [], [], []
for i, (nama, pulau, nk, (lon0, lat0), d) in enumerate(P):
    kp = str(11 + i)
    cols = math.ceil(math.sqrt(nk))
    rws = math.ceil(nk / cols)
    boxes.append((nama, lon0 - cols * CELL / 2, lon0 + cols * CELL / 2,
                  lat0 - rws * CELL / 2, lat0 + rws * CELL / 2))
    for j in range(nk):
        r, c = divmod(j, cols)
        x0 = lon0 - cols * CELL / 2 + c * CELL
        y0 = lat0 + rws * CELL / 2 - (r + 1) * CELL
        kode = f"{kp}{j + 1:02d}"
        ring = [[x0, y0], [x0 + CELL, y0], [x0 + CELL, y0 + CELL], [x0, y0 + CELL], [x0, y0]]
        feats.append({"type": "Feature", "properties": {"kode": kode},
                      "geometry": {"type": "Polygon", "coordinates": [ring]}})
        kota = rng.random() < 0.12
        loc = d + rng.normal(0, 0.5) + (0.8 if kota else 0)
        pop0 = rng.lognormal(12.6, 0.6) * (1.6 if kota else 1)
        luas = rng.lognormal(7.4, 0.9) * (0.05 if kota else 1) + 20
        for t in TAHUN:
            k = t - 2021
            pop = pop0 * (1 + 0.01 * k)
            miskin = float(np.clip(10.5 - 3.8 * loc - 0.3 * k + rng.normal(0, 0.7), 1.0, 45))
            krows.append(dict(
                kode=kode, kabkota=f"Kab/Kota Dummy {kp}-{j + 1:02d}", provinsi=nama,
                pulau=pulau, tahun=t,
                ipm=round(float(71 + 5 * loc + 0.8 * k + rng.normal(0, 0.5)), 2),
                miskin_persen=round(miskin, 2),
                penduduk=int(pop), luas_km2=round(float(luas), 1),
                kepadatan=round(float(pop / luas), 1),
                jml_miskin=round(float(pop * miskin / 100 / 1000), 2),  # ribu jiwa
                lon=round(x0 + CELL / 2, 4), lat=round(y0 + CELL / 2, 4),
            ))
kab = pd.DataFrame(krows)
kab.to_csv(OUT / "kabkota_panel.csv", index=False)
(OUT / "kabkota.geojson").write_text(
    json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")

# cek tumpang tindih kotak antarprovinsi (hanya peringatan)
for a in range(len(boxes)):
    for b in range(a + 1, len(boxes)):
        A, B = boxes[a], boxes[b]
        if A[1] < B[2] and B[1] < A[2] and A[3] < B[4] and B[3] < A[4]:
            print("tumpang tindih:", A[0], B[0])

# ---------- log sumber & metadata ----------
pd.DataFrame([
    ["DUMMY: Indeks Pembangunan Manusia menurut Provinsi", "2021-2025", "-", "-", "Data karangan acak"],
    ["DUMMY: indikator lain (UHH, HLS, RLS, dst.)", "2021-2025", "-", "-", "Data karangan acak"],
    ["DUMMY: indikator kab/kota", "2021-2025", "-", "-", "Data karangan acak"],
    ["DUMMY: batas wilayah (grid persegi)", "-", "-", "-", "Bukan batas wilayah sebenarnya"],
], columns=["judul", "tahun", "url", "tanggal_akses", "catatan"]).to_csv(OUT / "sumber.csv", index=False)
(OUT / "meta.json").write_text(json.dumps(
    {"dummy": True, "tahun_awal": 2021, "tahun_akhir": 2025}), encoding="utf-8")

print("provinsi:", prov.kode.nunique(), "| kab/kota:", kab.kode.nunique(), "| baris kab:", len(kab))
