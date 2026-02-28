import streamlit as st
import google.generativeai as genai
import re

# ==============================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Area Kertas Putih untuk Hasil RPP */
    .rpp-paper { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 40px 60px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 11pt;
        line-height: 1.5;
        border-radius: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .rpp-paper h1 { text-align: center; text-decoration: underline; font-size: 16pt; color: #000; text-transform: uppercase; margin-bottom: 20px; }
    .rpp-paper table { width: 100%; border-collapse: collapse; margin-bottom: 15px; background-color: white !important; }
    .rpp-paper th, .rpp-paper td { border: 1px solid black !important; padding: 8px 12px; text-align: left; color: #000 !important; vertical-align: top; }
    
    /* CSS KHUSUS TANDA TANGAN & IDENTITAS (TANPA GARIS) */
    .rpp-paper .no-border, .rpp-paper .no-border td { border: none !important; padding: 2px 0; }
    .name-line { font-weight: bold; text-decoration: underline; margin-bottom: 0px; padding-bottom: 0px; display: block; }
    .nip-line { margin-top: -5px; padding-top: 0px; font-size: 10pt; display: block; }

    @media print {
        .stButton, .stForm, .stMarkdown:not(.rpp-paper), .stSidebar, header, footer, .main-header, [data-testid="stHeader"] {
            display: none !important;
        }
        .stApp { background-color: white !important; }
        .rpp-paper { box-shadow: none; border: none; padding: 0; margin: 0; width: 100%; }
        table { page-break-inside: auto; }
        tr { page-break-inside: avoid; page-break-after: auto; }
        @page { size: auto; margin: 1.5cm; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SISTEM KEAMANAN & INPUT API KEY
# ==============================
with st.sidebar:
    st.header("🔑 ATUR CINTA")
    user_api_key = st.text_input("Ganti Dengan CINTA Baru", type="password", help="CINTA BARU jika jalur utama limit atau error 429.")
    st.divider()
    st.info("Prioritas: CINTA di atas. Jika kosong, menggunakan CINTA BARU (Secrets).")

FINAL_API_KEY = user_api_key if user_api_key else st.secrets.get("GEMINI_API_KEY", "")

if not FINAL_API_KEY:
    st.error("⚠️ API Key tidak ditemukan! Silakan masukkan API Key di Sidebar untuk memulai.")
    st.stop()

genai.configure(api_key=FINAL_API_KEY)

if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
MAX_FREE_TRIAL = 5

# ==============================
# 3. INTERFACE (HEADER)
# ==============================
st.markdown(f"""
    <div class="main-header" style="background-color:#007BFF;padding:20px;border-radius:10px;text-align:center;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">AI RPP GENERATOR PRO</h1>
        <p style="color:white;font-weight:bold;margin:5px;">Karya: ANDY KURNIAWAN (WA: 081338370402)</p>
    </div>
""", unsafe_allow_html=True)

if st.session_state.usage_count >= MAX_FREE_TRIAL:
    st.error("🚫 BATAS PENGGUNAAN GRATIS TERCAPAI. Hubungi Pak Andy Kurniawan (081338370402) untuk aktivasi Full.")
    st.stop()

# ==============================
# 4. FORM INPUT (100% DIPERTAHANKAN)
# ==============================
with st.form("main_form"):
    st.subheader("🏢 Data Administrasi Sekolah")
    c1, c2 = st.columns(2)
    with c1:
        nama_sekolah = st.text_input("Nama Sekolah", placeholder="SD Negeri ...")
        nama_kepsek = st.text_input("Nama Kepala Sekolah")
        nip_kepsek = st.text_input("NIP Kepala Sekolah")
    with c2:
        nama_guru = st.text_input("Nama Guru")
        nip_guru = st.text_input("NIP Guru")
        mapel = st.selectbox("Mata Pelajaran", ["Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia", "Matematika", "IPAS", "Seni Musik", "Seni Rupa", "Seni Teater", "Seni Tari", "PJOK", "Bahasa Inggris", "Muatan Lokal"])

    st.subheader("🌟 Dimensi Profil Lulusan")
    cp1, cp2 = st.columns(2)
    with cp1:
        p1 = st.checkbox("Keimanan & Ketakwaan Kepada Tuhan YME")
        p2 = st.checkbox("Kewargaan (Berkebinekaan Global)")
        p3 = st.checkbox("Penalaran Kritis")
        p4 = st.checkbox("Kreativitas")
    with cp2:
        p5 = st.checkbox("Kolaborasi (Gotong Royong)")
        p6 = st.checkbox("Kemandirian")
        p7 = st.checkbox("Kesehatan")
        p8 = st.checkbox("Komunikasi")

    st.subheader("📖 Sumber & Media Belajar")
    cm1, cm2 = st.columns(2)
    with cm1:
        media_ajar = st.text_area("Media Pembelajaran", placeholder="Contoh: LCD Proyektor, Video YouTube, Kartu Gambar...")
    with cm2:
        sumber_ajar = st.text_area("Sumber Belajar", placeholder="Contoh: Buku Siswa Kelas 4, Lingkungan Sekolah...")

    st.subheader("📅 Rincian Pertemuan")
    fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    jml_pertemuan = st.number_input("Jumlah Pertemuan", 1, 15, 1)

    list_model = ["PBL (Problem Based Learning)", "PjBL (Project Based Learning)", "Discovery Learning", "Inquiry Learning", "Contextual Learning", "STAD", "Demonstrasi", "Mind Mapping", "Role Playing", "Think Pair Share", "Problem Solving", "Blended Learning", "Flipped Classroom", "Project Citizen", "Ceramah Plus"]

    data_pertemuan = []
    for i in range(int(jml_pertemuan)):
        with st.expander(f"📍 Konfigurasi Pertemuan Ke-{i+1}", expanded=(i==0)):
            ca, cb, cc = st.columns([2,1,1])
            with ca: m = st.selectbox(f"Model P{i+1}", list_model, key=f"m_{i}")
            with cb: w = st.text_input(f"Waktu P{i+1}", "2x35 Menit", key=f"w_{i}")
            with cc: t = st.text_input(f"Tanggal P{i+1}", placeholder="DD-MM-YYYY", key=f"t_{i}")
            data_pertemuan.append({"no": i+1, "model": m, "waktu": w, "tgl": t})

    tujuan_umum = st.text_area("Tujuan Pembelajaran")
    materi_pokok = st.text_area("Detail Materi Pokok (CP/ATP)")
    
    btn_generate = st.form_submit_button("🚀 GENERATE RPP SEKARANG")

# ==============================
# 5. LOGIKA GENERATE (SEMPURNA & BERSIH)
# ==============================
if btn_generate:
    if not nama_sekolah or not materi_pokok:
        st.warning("⚠️ Mohon lengkapi Data Sekolah dan Materi!")
    else:
        model_variants = ['gemini-2.0-flash-001', 'gemini-1.5-flash', 'gemini-1.5-flash-8b']
        
        profil_str = ", ".join([k for k, v in {"Beriman":p1, "Kewargaan":p2, "Bernalar Kritis":p3, "Kreatif":p4, "Gotong Royong":p5, "Mandiri":p6, "Kesehatan":p7, "Komunikasi":p8}.items() if v])
        jadwal_detail = "\n".join([f"- P{p['no']}: Model {p['model']}, Waktu {p['waktu']}, Tgl {p['tgl']}" for p in data_pertemuan])
        
        # PROMPT YANG LEBIH TEGAS AGAR HASIL TIDAK BERANTAKAN
        prompt = f"""
        Buatlah RPP Kurikulum Merdeka HOLISTIK dalam format HTML MURNI.
        DILARANG memberikan kata pengantar, DILARANG menggunakan markdown ```html.
        Langsung mulai dari tag HTML untuk konten RPP.

        DATA:
        Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
        Mapel: {mapel} | Fase: {fase} | Materi: {materi_pokok}
        Dimensi Profil: {profil_str} | Media: {media_ajar} | Sumber: {sumber_ajar}
        Jadwal: {jadwal_detail} | Tujuan: {tujuan_umum}

        STRUKTUR WAJIB:
        1. Judul: <h1>MODUL AJAR / RPP KURIKULUM MERDEKA</h1>
        2. Identitas Sekolah & Komponen Inti (Media/Sumber) dalam <table class="no-border">.
        3. Langkah Pembelajaran dalam <table border="1">.
           - Pendahuluan (Apersepsi Bermakna)
           - Inti (Sesuai Sintaks {list_model[0]})
           - Penutup (Refleksi Murid)
        4. Asesmen & Rubrik Penilaian Lengkap.
        5. Tanda Tangan rapat dengan class="name-line" dan class="nip-line".
        """

        success = False
        for m_name in model_variants:
            try:
                with st.spinner(f"Menyusun RPP via {m_name}..."):
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(prompt)
                    raw_text = response.text
                    
                    # LOGIKA PEMBERSIH (CLEANING): Membuang ```html dan spasi tak perlu
                    clean_html = re.sub(r'```html|```', '', raw_text).strip()
                    
                    if clean_html:
                        st.session_state.usage_count += 1
                        st.session_state.hasil_rpp = clean_html
                        success = True
                        break
            except Exception as e:
                if "429" in str(e): continue
                else: 
                    st.error(f"Error: {e}")
                    break

        if not success:
            st.error("⚠️ Semua jalur API limit. Silakan masukkan API Key baru di Sidebar!")

# ==============================
# 6. DISPLAY HASIL
# ==============================
if "hasil_rpp" in st.session_state:
    st.success(f"✅ RPP Selesai! (Sisa: {MAX_FREE_TRIAL - st.session_state.usage_count})")
    st.markdown("""<button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px; margin-bottom:10px;">📥 DOWNLOAD / CETAK SEBAGAI PDF</button>""", unsafe_allow_html=True)
    
    # Menampilkan hasil di dalam kertas putih
    st.markdown(f'<div class="rpp-paper">{st.session_state.hasil_rpp}</div>', unsafe_allow_html=True)

st.markdown(f"<br><p style='text-align: center; color: #555;'>© 2026 AI Generator Pro - Andy Kurniawan</p>", unsafe_allow_html=True)
