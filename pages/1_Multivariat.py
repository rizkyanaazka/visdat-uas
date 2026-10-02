import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.cluster.hierarchy import leaves_list, linkage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import utils as U

st.set_page_config(page_title="Siapa yang tertinggal?", layout="wide")
U.banner()

df = U.provinsi()
m = U.meta()
VAR = [v for v in U.LABEL if v in df.columns]

st.title("Siapa yang tertinggal? Profil provinsi")

# ---------- kontrol ----------
st.sidebar.header("Pengaturan")
tahun = st.sidebar.slider("Tahun", m["tahun_awal"], m["tahun_akhir"], m["tahun_akhir"])
pilih = st.sidebar.multiselect(
    "Variabel untuk PCA", VAR, default=[v for v in VAR if v != "ipm"], format_func=U.LABEL.get,
    help="IPM dikeluarkan secara bawaan karena dihitung dari variabel lain (UHH, HLS, RLS, pengeluaran).")
k = st.sidebar.slider("Jumlah klaster (K-Means)", 2, 5, 3)
if len(pilih) < 3:
    st.warning("Pilih minimal 3 variabel.")
    st.stop()

# ---------- PCA: skala dan sumbu dipelajari dari seluruh tahun agar antartahun sebanding ----------
scaler = StandardScaler().fit(df[pilih])
pca = PCA(n_components=2).fit(scaler.transform(df[pilih]))
cur = df[df.tahun == tahun].reset_index(drop=True)
Z = scaler.transform(cur[pilih])
cur[["PC1", "PC2"]] = pca.transform(Z)
ev = pca.explained_variance_ratio_ * 100

# klaster diberi nama berdasarkan urutan rata-rata IPM agar stabil dan mudah dibaca
lab = KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(Z)
urut = cur.groupby(lab).ipm.mean().sort_values(ascending=False).index.tolist()
nama = {c: f"Klaster {chr(65 + i)}" for i, c in enumerate(urut)}
cur["Klaster"] = [nama[c] for c in lab]
rata = cur.groupby("Klaster").ipm.mean().round(1)

# pencilan: jarak terjauh dari pusat di bidang PC1-PC2
jarak = np.hypot(cur.PC1 - cur.PC1.mean(), cur.PC2 - cur.PC2.mean())
pencilan = cur.assign(jarak=jarak).nlargest(3, "jarak").provinsi.tolist()
beban = pd.DataFrame(pca.components_.T, index=pilih, columns=["PC1", "PC2"])
dom = beban.PC1.abs().sort_values(ascending=False).index[:2].tolist()

st.markdown(
    f"**{tahun}:** PC1 menjelaskan {ev[0]:.0f}% variasi, didominasi "
    f"{U.LABEL[dom[0]].split(' (')[0].lower()} dan {U.LABEL[dom[1]].split(' (')[0].lower()}. "
    f"Provinsi paling menyimpang dari pola umum: {', '.join(pencilan)}.")

# ---------- tampilan 1 dan 2: PCA (sumber seleksi) dan parallel coordinates (target) ----------
kiri, kanan = st.columns(2)
with kiri:
    st.subheader("PCA: posisi provinsi")
    fig = px.scatter(
        cur, x="PC1", y="PC2", color="Klaster", hover_name="provinsi",
        custom_data=["kode"], color_discrete_sequence=U.OKABE,
        category_orders={"Klaster": sorted(cur.Klaster.unique())},
        hover_data={"ipm": ":.1f", "miskin": ":.1f", "PC1": False, "PC2": False},
        labels={"PC1": f"PC1 ({ev[0]:.0f}%)", "PC2": f"PC2 ({ev[1]:.0f}%)",
                "ipm": "IPM", "miskin": "Miskin (%)"})
    fig.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))
    fig.update_layout(dragmode="lasso", height=430, margin=dict(l=0, r=0, t=10, b=0))
    sel = st.plotly_chart(fig, on_select="rerun", selection_mode=("box", "lasso", "points"),
                          key="pca", width="stretch")
    terpilih = [p["customdata"][0] for p in sel.selection["points"]]
    if terpilih:
        st.caption(f"{len(terpilih)} provinsi dipilih. Klik area kosong pada grafik untuk membatalkan.")
    else:
        st.caption("Pilih titik dengan box atau lasso untuk menyorotnya di grafik lain.")
    st.caption("Posisi = kemiripan profil; warna = klaster K-Means (Okabe-Ito).")

cur["pilih"] = cur.kode.isin(terpilih).astype(int) if terpilih else 1

with kanan:
    st.subheader("Parallel coordinates")
    skala = [[0, "#BDBDBD"], [1, "#D55E00"]] if terpilih else [[0, "#0072B2"], [1, "#0072B2"]]
    pc = go.Figure(go.Parcoords(
        line=dict(color=cur["pilih"], colorscale=skala, cmin=0, cmax=1),
        dimensions=[dict(label=v, values=cur[v]) for v in pilih]))
    pc.update_layout(height=430, margin=dict(l=40, r=40, t=50, b=10))
    st.plotly_chart(pc, width="stretch")
    st.caption("Satu garis = satu provinsi; oranye = provinsi yang dipilih. "
               "Seret pada sumbu untuk menyaring.")

# ---------- tampilan 3: heatmap terklaster (ikut seleksi) ----------
st.subheader("Heatmap terklaster")
H = pd.DataFrame(Z, columns=pilih, index=cur.provinsi)
if terpilih:
    H = H[cur.kode.isin(terpilih).values]
if len(H) >= 2:
    H = H.iloc[leaves_list(linkage(H.values, "ward"))]
H.columns = [c for c in H.columns]
hm = px.imshow(H, color_continuous_scale="RdBu_r", color_continuous_midpoint=0, aspect="auto",
               labels=dict(color="z-score", x="Variabel", y="Provinsi"))
hm.update_layout(height=max(360, 18 * len(H) + 120), margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(hm, width="stretch")
st.caption("Nilai dibakukan (z-score): merah di atas rata-rata nasional, biru di bawahnya. "
           "Baris diurutkan menurut kemiripan (Ward). Heatmap hanya memuat provinsi yang dipilih di PCA.")

# ---------- interpretasi ----------
with st.expander("Interpretasi klaster dan loading PCA"):
    st.write("Rata-rata IPM per klaster:", ", ".join(f"{i} = {v}" for i, v in rata.items()))
    st.dataframe(beban.style.format("{:.2f}"), width="stretch")
    st.caption("Loading menunjukkan variabel mana yang membentuk tiap komponen. "
               "Tulis tafsirmu sendiri untuk bagian Hasil dan Pembahasan.")
U.sumber_bps(f"Data tahun {tahun}; variabel dibakukan sebelum PCA agar satuan tidak mendominasi.")
