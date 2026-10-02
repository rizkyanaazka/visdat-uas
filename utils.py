"""Fungsi bersama: memuat data, label, palet, dan elemen tampilan."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"

# Palet Okabe-Ito (aman untuk buta warna) untuk kategori; Viridis untuk skala berurutan
OKABE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
PULAU_URUT = ["Sumatera", "Jawa", "Bali dan Nusa Tenggara", "Kalimantan", "Sulawesi", "Maluku", "Papua"]
WARNA_PULAU = dict(zip(PULAU_URUT, OKABE))

LABEL = {
    "ipm": "IPM (indeks)",
    "uhh": "Umur harapan hidup (tahun)",
    "hls": "Harapan lama sekolah (tahun)",
    "rls": "Rata-rata lama sekolah (tahun)",
    "pengeluaran": "Pengeluaran per kapita disesuaikan (ribu Rp)",
    "miskin": "Penduduk miskin (%)",
    "tpt": "Tingkat pengangguran terbuka (%)",
    "tpak": "Tingkat partisipasi angkatan kerja (%)",
    "gini": "Gini ratio",
    "sanitasi": "Rumah tangga sanitasi layak (%)",
    "air_minum": "Rumah tangga air minum layak (%)",
}
LABEL_KAB = {
    "miskin_persen": "Penduduk miskin (%)",
    "ipm": "IPM (indeks)",
    "kepadatan": "Kepadatan penduduk (jiwa/km²)",
}


@st.cache_data
def meta():
    return json.loads((DATA / "meta.json").read_text(encoding="utf-8"))


@st.cache_data
def provinsi():
    return pd.read_csv(DATA / "provinsi_panel.csv", dtype={"kode": str})


@st.cache_data
def kabkota():
    return pd.read_csv(DATA / "kabkota_panel.csv", dtype={"kode": str})


@st.cache_data
def geojson():
    return json.loads((DATA / "kabkota.geojson").read_text(encoding="utf-8"))


@st.cache_data
def sumber():
    return pd.read_csv(DATA / "sumber.csv")


def banner():
    """Tampilkan peringatan selama data masih dummy (diatur di data/meta.json)."""
    if meta().get("dummy"):
        st.warning("**Data dummy.** Angka, kode wilayah, dan peta pada prototipe ini "
                   "karangan acak, bukan data BPS. Jangan dikutip.")


def sumber_bps(catatan=""):
    teks = "Sumber: BPS."
    if meta().get("dummy"):
        teks = "Sumber: BPS (placeholder, saat ini data dummy)."
    st.caption(f"{teks} {catatan}".strip())
