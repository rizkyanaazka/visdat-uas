# Ketimpangan Pembangunan Manusia Antarwilayah Indonesia (prototipe)

Tautan aplikasi: (isi setelah deploy)

> **Status: data masih DUMMY.** Semua angka, kode wilayah, dan poligon peta dibuat acak oleh
> `make_dummy_data.py`. Tandanya `"dummy": true` di `data/meta.json`; selama itu `true`, setiap
> halaman menampilkan peringatan. Ganti data, lalu ubah menjadi `false`.

## Isi
| Halaman | Topik visualisasi | Teknik |
|---|---|---|
| Beranda | pengantar cerita | temuan kunci otomatis, tren IPM per pulau |
| 1 Multivariat | data berdimensi tinggi | PCA, parallel coordinates, heatmap terklaster, brushing dan linking |
| 2 Geospasial | data geospasial | choropleth (rasio, kelas tetap antartahun), lingkaran proporsional, kontrol layer |
| 3 Hierarkis | data hierarkis | treemap dan sunburst, pulau → provinsi → kab/kota, drill-down dan breadcrumb |
| 4 Penutup | - | kesimpulan, keterbatasan, daftar sumber |

## Menjalankan
```
pip install -r requirements.txt
python make_dummy_data.py      # hanya untuk data dummy
streamlit run app.py
```

## Mengganti dengan data BPS asli
Taruh file berikut di `data/` (semua kolom `kode` bertipe teks), lalu set `"dummy": false` di `meta.json`
dan hapus `make_dummy_data.py`.

| File | Kolom wajib |
|---|---|
| `provinsi_panel.csv` | `kode, provinsi, pulau, tahun, ipm, uhh, hls, rls, pengeluaran, miskin, tpt, tpak, gini, sanitasi, air_minum` (minimal 8 variabel numerik, minimal 34 provinsi) |
| `kabkota_panel.csv` | `kode, kabkota, provinsi, pulau, tahun, ipm, miskin_persen, penduduk, luas_km2, kepadatan, jml_miskin (ribu jiwa), lon, lat` |
| `kabkota.geojson` | fitur dengan properti `kode` yang cocok persis dengan `kode` di CSV |
| `sumber.csv` | `judul, tahun, url, tanggal_akses, catatan` |
| `meta.json` | `{"dummy": false, "tahun_awal": 2021, "tahun_akhir": 2025}` |

Nama pulau harus salah satu dari: Sumatera, Jawa, Bali dan Nusa Tenggara, Kalimantan, Sulawesi, Maluku, Papua
(atau ubah `PULAU_URUT` di `utils.py`). Variabel di `LABEL` (`utils.py`) yang tidak ada di CSV otomatis dilewati.

## Data
| Judul tabel | Tahun | URL | Tanggal akses |
|---|---|---|---|
| (isi) | | | |

## Pra-pemrosesan
(Jelaskan `preprocess.py` dan cara menjalankannya ulang.)

## Rancangan visual
(Topik, teknik, encoding, palet: Okabe-Ito untuk kategori, Viridis untuk skala berurutan, RdBu untuk skala divergen.)

## Deklarasi penggunaan AI
(Isi dengan kenyataan pengerjaanmu: alat apa, untuk apa, dan apa yang kamu verifikasi dan ubah sendiri.)
