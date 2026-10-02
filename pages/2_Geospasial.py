import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import utils as U

st.set_page_config(page_title="Di mana letaknya?", layout="wide")
U.banner()

kab = U.kabkota()
gj = U.geojson()
m = U.meta()

st.title("Di mana letaknya? Peta kabupaten/kota")

# ---------- kontrol ----------
st.sidebar.header("Pengaturan peta")
tahun = st.sidebar.slider("Tahun", m["tahun_awal"], m["tahun_akhir"], m["tahun_akhir"])
ind = st.sidebar.selectbox("Indikator (rasio)", list(U.LABEL_KAB), format_func=U.LABEL_KAB.get)
metode = st.sidebar.radio("Klasifikasi", ["Kuantil", "Interval sama"],
                          help="Kuantil: jumlah daerah tiap kelas hampir sama. "
                               "Interval sama: lebar tiap kelas sama.")
n = st.sidebar.slider("Jumlah kelas", 3, 7, 5)
st.sidebar.markdown("**Layer**")
tampil_choro = st.sidebar.checkbox("Choropleth (rasio)", value=True)
tampil_simbol = st.sidebar.checkbox("Lingkaran proporsional (jumlah penduduk miskin)", value=False)
pulau = st.sidebar.multiselect("Filter pulau", U.PULAU_URUT)

# ---------- klasifikasi: batas kelas dihitung dari seluruh tahun agar warna sebanding antartahun ----------
semua = kab[ind].dropna()
if metode == "Kuantil":
    batas = np.unique(np.quantile(semua, np.linspace(0, 1, n + 1)))
else:
    batas = np.linspace(semua.min(), semua.max(), n + 1)
nk = len(batas) - 1
fmt = "{:,.0f}" if ind == "kepadatan" else "{:.1f}"
label_kelas = [f"{fmt.format(batas[i])}-{fmt.format(batas[i + 1])}" for i in range(nk)]

d = kab[kab.tahun == tahun].copy()
if pulau:
    d = d[d.pulau.isin(pulau)]
d["kelas"] = np.clip(np.digitize(d[ind], batas[1:-1], right=True), 0, nk - 1)

# peringatan jika kode data tidak cocok dengan GeoJSON
kode_geo = {f["properties"]["kode"] for f in gj["features"]}
tak_cocok = set(d.kode) - kode_geo
if tak_cocok:
    st.error(f"{len(tak_cocok)} kode kab/kota tidak ada di GeoJSON, contoh: {sorted(tak_cocok)[:5]}")

# ---------- ringkasan teks ----------
atas = d.nlargest(1, ind).iloc[0]
bawah = d.nsmallest(1, ind).iloc[0]
st.markdown(
    f"**{tahun}, {U.LABEL_KAB[ind].lower()}:** tertinggi di {atas.kabkota} "
    f"({atas[ind]:,.1f}), terendah di {bawah.kabkota} ({bawah[ind]:,.1f}). "
    f"Menampilkan {len(d)} kabupaten/kota.")

# ---------- peta ----------
fig = go.Figure()
if tampil_choro:
    warna = px.colors.sample_colorscale("Viridis", [i / max(nk - 1, 1) for i in range(nk)])
    skala = []
    for i, w in enumerate(warna):
        skala += [[i / nk, w], [(i + 1) / nk, w]]
    fig.add_trace(go.Choroplethmap(
        geojson=gj, locations=d.kode, featureidkey="properties.kode", z=d.kelas,
        zmin=-0.5, zmax=nk - 0.5, colorscale=skala, marker_opacity=0.8, marker_line_width=0.3,
        customdata=np.stack([d.kabkota, d.provinsi, d[ind]], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                      + U.LABEL_KAB[ind] + ": %{customdata[2]:,.1f}<extra></extra>",
        colorbar=dict(title=U.LABEL_KAB[ind], tickvals=list(range(nk)), ticktext=label_kelas,
                      len=0.8, thickness=14)))
if tampil_simbol:
    maks = np.sqrt(kab.jml_miskin.max())
    fig.add_trace(go.Scattermap(
        lat=d.lat, lon=d.lon, mode="markers",
        marker=dict(size=np.sqrt(d.jml_miskin) / maks * 34 + 3, color="#D55E00", opacity=0.6),
        customdata=np.stack([d.kabkota, d.jml_miskin], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Penduduk miskin: %{customdata[1]:,.1f} ribu jiwa<extra></extra>",
        name="Penduduk miskin (ribu jiwa)", showlegend=False))
fig.update_layout(map=dict(style="carto-positron", zoom=3.4, center=dict(lat=-2.5, lon=118)),
                  height=560, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, width="stretch")
if not (tampil_choro or tampil_simbol):
    st.info("Nyalakan minimal satu layer di menu samping.")
st.caption("Warna = kelas indikator (batas kelas tetap untuk semua tahun); "
           "lingkaran = jumlah penduduk miskin, luasnya sebanding dengan jumlah. "
           "Gunakan scroll atau cubit untuk zoom, seret untuk menggeser.")

# ---------- 10 daerah tertinggi ----------
with st.expander(f"10 kabupaten/kota dengan {U.LABEL_KAB[ind].lower()} tertinggi, {tahun}"):
    top = d.nlargest(10, ind)[["kabkota", "provinsi", ind, "jml_miskin"]]
    top.columns = ["Kabupaten/kota", "Provinsi", U.LABEL_KAB[ind], "Penduduk miskin (ribu jiwa)"]
    st.dataframe(top, hide_index=True, width="stretch")
U.sumber_bps("Batas wilayah: non-BPS (isi sumber dan lisensi di README).")
