import plotly.express as px
import streamlit as st

import utils as U

st.set_page_config(page_title="Ketimpangan Pembangunan Manusia", layout="wide")
U.banner()

prov = U.provinsi()
kab = U.kabkota()
m = U.meta()
t0, t1 = m["tahun_awal"], m["tahun_akhir"]

st.title("Seberapa timpang pembangunan manusia antarwilayah Indonesia?")
st.write(
    f"Cerita data {t0}-{t1} dalam tiga langkah: **siapa** yang tertinggal (profil provinsi), "
    "**di mana** letaknya (peta kabupaten/kota), dan **seberapa besar** beban kemiskinannya "
    "(hierarki pulau, provinsi, kabupaten/kota). Buka halaman di menu samping secara berurutan."
)

# ---------- temuan kunci, dihitung otomatis dari data ----------
a = prov[prov.tahun == t1].sort_values("ipm")
b = prov[prov.tahun == t0].sort_values("ipm")
selisih1 = a.ipm.iloc[-1] - a.ipm.iloc[0]
selisih0 = b.ipm.iloc[-1] - b.ipm.iloc[0]

kt = kab[kab.tahun == t1]
g = kt.groupby("pulau")
persen = (g.apply(lambda x: (x.penduduk * x.miskin_persen).sum() / x.penduduk.sum(),
                  include_groups=False)).sort_values()
absolut = g.jml_miskin.sum().sort_values()

c1, c2, c3 = st.columns(3)
c1.metric(f"Selisih IPM tertinggi-terendah, {t1}", f"{selisih1:.1f} poin",
          f"{selisih1 - selisih0:+.1f} dibanding {t0}", delta_color="inverse")
c1.caption(f"{a.provinsi.iloc[-1]} (tertinggi) vs {a.provinsi.iloc[0]} (terendah).")
c2.metric("Pulau dengan persentase miskin tertinggi", persen.index[-1], f"{persen.iloc[-1]:.1f}%",
          delta_color="off")
c2.caption(f"Terendah: {persen.index[0]} ({persen.iloc[0]:.1f}%). Rata-rata tertimbang penduduk kab/kota.")
c3.metric("Pulau dengan jumlah penduduk miskin terbesar", absolut.index[-1],
          f"{absolut.iloc[-1]:,.0f} ribu jiwa", delta_color="off")
c3.caption("Jumlah absolut dan persentase bisa menunjuk pulau yang berbeda.")

st.caption("Angka di atas dihitung otomatis dari data di folder data/. "
           "Tafsirkan dan tulis ulang temuan dengan kata-katamu sendiri setelah memakai data BPS asli.")

# ---------- tren ----------
st.subheader("IPM rata-rata per pulau")
tren = prov.groupby(["tahun", "pulau"], as_index=False).ipm.mean()
fig = px.line(tren, x="tahun", y="ipm", color="pulau", markers=True,
              category_orders={"pulau": U.PULAU_URUT}, color_discrete_map=U.WARNA_PULAU,
              labels={"ipm": "IPM (rata-rata provinsi)", "tahun": "Tahun", "pulau": "Pulau"})
fig.update_xaxes(dtick=1)
fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0), legend_title_text="Pulau")
st.plotly_chart(fig, width="stretch")
U.sumber_bps("Rata-rata sederhana IPM provinsi per pulau.")

st.subheader("Cara membaca")
st.markdown(
    "- **Multivariat:** setiap titik adalah satu provinsi. Titik yang berdekatan punya profil serupa.\n"
    "- **Geospasial:** peta berwarna memakai persentase (rasio), lingkaran memakai jumlah orang.\n"
    "- **Hierarkis:** luas kotak = jumlah penduduk miskin, warna = persentase miskin."
)
