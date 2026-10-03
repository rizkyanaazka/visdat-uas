# Tiga Bekal Hidup — Kisah IPM Indonesia 2021–2025
Web storytelling interaktif (UAS Visualisasi Data dan Informasi 2026). Pembaca cukup menggulir; tahun, pulau, dan provinsi diatur lewat panel di bawah layar.

**Alur cerita:** pengenalan, tren per pulau, pilihan tahun/lokus, lalu klimaks dan penutup. Tema gelap/terang bisa dipilih pengguna.

**Topik visualisasi:** multivariat (PCA + biplot + parallel coordinates + heatmap, brushing & linking), geospasial (peta titik 514 kab/kota: warna & simbol proporsional), hierarkis (treemap + sunburst 4 level, drill-down & breadcrumb).

## Struktur
- `index.html` — tampilan & logika (D3 v7 via jsDelivr, cadangan cdnjs; tanpa build step)
- `data.js` — data terolah, dibuat oleh `scripts/build_data.py`
- `data/raw/` — berkas Excel asli (provinsi & kab/kota)

## Menjalankan
`python -m http.server` lalu buka http://localhost:8000. Bangun ulang data: `python scripts/build_data.py`.
Deploy: Settings → Pages → Deploy from branch (`main`, `/root`).

## Sumber data (ISI SEBELUM DIKUMPULKAN)
| Judul tabel/publikasi | Tahun data | URL | Tanggal akses |
|---|---|---|---|
| … | 2021–2025 | … | … |

## Catatan data
- **Koreksi:** luas Kota Ambon pada berkas mentah 35.944,62 km² (selisih 100×) dikoreksi menjadi 359,45 km² di `scripts/build_data.py`; berkas mentah tidak diubah. Verifikasi ke publikasi BPS.
- **Papua:** IPM 2021–2022 mengukur wilayah sebelum pemekaran (2022), sehingga tidak dibandingkan dengan 2023–2025.
- Jumlah penduduk pada treemap/sunburst adalah proksi (kepadatan × luas wilayah); luas sebagian kabupaten kepulauan dapat mencakup perairan.
Empat provinsi baru (Papua Selatan, Tengah, Pegunungan, Barat Daya) umumnya baru bernilai sejak 2023; Rasio Gini 2023 kosong ('-'); kemiskinan sebagian kab/kota baru kosong 2021–2023. PCA 2021–2022 memakai 34 provinsi; nilai kosong lain diimputasi rata-rata.

## Deklarasi alat bantu AI
Claude (Anthropic) dipakai membantu menyusun kode awal web. Sesuaikan dengan penggunaan sebenarnya di bagian Metodologi makalah.
