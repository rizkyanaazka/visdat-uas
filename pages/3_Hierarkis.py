import plotly.express as px
import streamlit as st

import utils as U

st.set_page_config(page_title="Seberapa besar bebannya?", layout="wide")
U.banner()

kab = U.kabkota()
m = U.meta()

st.title("Seberapa besar bebannya? Pulau, provinsi, kabupaten/kota")

# ---------- kontrol drill-down ----------
st.sidebar.header("Telusuri")
tahun = st.sidebar.slider("Tahun", m["tahun_awal"], m["tahun_akhir"], m["tahun_akhir"])
pulau = st.sidebar.selectbox("Pulau", ["Semua"] + U.PULAU_URUT)
d = kab[kab.tahun == tahun].copy()
if pulau != "Semua":
    d = d[d.pulau == pulau]
prov = st.sidebar.selectbox("Provinsi", ["Semua"] + sorted(d.provinsi.unique()))
if prov != "Semua":
    d = d[d.provinsi == prov]

# penunjuk posisi (breadcrumb) yang berlaku untuk kedua tampilan
posisi = ["Indonesia"] + ([pulau] if pulau != "Semua" else []) + ([prov] if prov != "Semua" else [])
st.markdown("**Posisi:** " + " › ".join(posisi))

d.insert(0, "Indonesia", "Indonesia")
jalur = ["Indonesia", "pulau", "provinsi", "kabkota"]
rentang = (float(kab.miskin_persen.min()), float(kab.miskin_persen.max()))
total = d.jml_miskin.sum()
persen = (d.penduduk * d.miskin_persen).sum() / d.penduduk.sum()
st.markdown(f"**{tahun}:** {total:,.0f} ribu penduduk miskin di {len(d)} kabupaten/kota, "
            f"dengan persentase miskin tertimbang {persen:.1f}%.")

label = {"jml_miskin": "Penduduk miskin (ribu jiwa)", "miskin_persen": "Miskin (%)"}
t1, t2 = st.tabs(["Treemap", "Sunburst"])
with t1:
    f = px.treemap(d, path=jalur, values="jml_miskin", color="miskin_persen",
                   color_continuous_scale="Viridis", range_color=rentang, labels=label)
    f.update_traces(pathbar_visible=True,
                    hovertemplate="<b>%{label}</b><br>Penduduk miskin: %{value:,.0f} ribu jiwa"
                                  "<br>Miskin: %{color:.1f}%<extra></extra>")
    f.update_layout(height=560, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(f, width="stretch")
with t2:
    f2 = px.sunburst(d, path=jalur, values="jml_miskin", color="miskin_persen",
                     color_continuous_scale="Viridis", range_color=rentang, labels=label, maxdepth=3)
    f2.update_traces(hovertemplate="<b>%{label}</b><br>Penduduk miskin: %{value:,.0f} ribu jiwa"
                                   "<br>Miskin: %{color:.1f}%<extra></extra>")
    f2.update_layout(height=560, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(f2, width="stretch")
st.caption("Luas = jumlah penduduk miskin; warna = persentase miskin (skala sama untuk semua tahun). "
           "Klik sebuah kotak atau irisan untuk masuk lebih dalam, atau pakai menu Pulau dan Provinsi. "
           "Luas besar dengan warna terang berarti beban absolut dan persentase sama-sama tinggi.")
U.sumber_bps("Hierarki wilayah administrasi; pengelompokan pulau dibuat penulis.")
