import streamlit as st

import utils as U

st.set_page_config(page_title="Penutup", layout="wide")
U.banner()

st.title("Penutup: apa artinya dan apa batasnya")

st.subheader("Kesimpulan")
st.info("Tulis 3-4 kalimat kesimpulanmu sendiri di sini setelah data BPS asli masuk dan kamu "
        "sudah melihat hasilnya di tiga halaman sebelumnya. Ubah teks ini di pages/4_Penutup.py.")

st.subheader("Keterbatasan")
st.markdown(
    "- Data kabupaten/kota dan provinsi berasal dari tabel BPS yang berbeda; definisi dan periode "
    "survei bisa tidak persis sama.\n"
    "- Pemekaran provinsi di Papua membuat jumlah unit berubah antartahun (cek bagian Metodologi).\n"
    "- PCA dan K-Means menyederhanakan profil; klaster tidak berarti batas yang tegas.\n"
    "- Batas kelas peta memengaruhi kesan visual; kuantil dan interval sama bisa memberi cerita berbeda."
)

st.subheader("Daftar sumber data")
st.dataframe(U.sumber().rename(columns={
    "judul": "Judul tabel/publikasi", "tahun": "Tahun data", "url": "URL",
    "tanggal_akses": "Tanggal akses", "catatan": "Catatan"}),
    hide_index=True, width="stretch")
U.sumber_bps()
