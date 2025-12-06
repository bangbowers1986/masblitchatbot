# app.py
import streamlit as st
import os
from rag_engine import retrieve
from gemini_client import ask_gemini
from utils.style_phrases import inject_humor
from utils.recommender import recommend

# === CONFIG ===
st.set_page_config(
    page_title="Mas Blit — Chatbot Budaya Blitar",
    page_icon="🏯",
    layout="centered"
)

# CSS custom
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
    .stButton>button {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Coat_of_arms_of_Blitarkab.png/120px-Coat_of_arms_of_Blitarkab.png", width=60)
with col2:
    st.title("🏯 Mas Blit")
    st.caption("Asisten Budaya Blitar — Santai, Lokal, & Ngeneni!")

st.markdown("Halo, aku **Mas Blit**! Mau ngobrol soal *sejarah, kuliner, festival*, atau *wisata* di Blitar? Ayo, tak ajak muter-muter kota Bung Karno! 😊")

# === SESSION STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo, aku Mas Blit! 😊 Mau ngobrol soal budaya Blitar? Ayo, tak ajak muter-muter kota Bung Karno!"
        }
    ]

# === TAMPILKAN CHAT ===
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# === INPUT USER ===
if prompt := st.chat_input("Contoh: 'Apa itu Grebeg Suro?' atau 'Rekomendasi kuliner khas Blitar?'"):
    # Simpan & tampilkan input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # === PROSES ===
    with st.chat_message("assistant"):
        with st.spinner("Mas Blit lagi mikir… 🤔"):
            # 1. RAG retrieval
            retrieved = retrieve(prompt, top_k=2)
            context_text = ""
            if retrieved:
                context_text = "\n\n".join([
                    f"[{i+1}] {doc['judul']}: {doc['konten']}"
                    for i, doc in enumerate(retrieved)
                ])

            # 2. Prompt ke Gemini
            system_prompt = f"""
Kamu adalah "Mas Blit", chatbot asisten budaya dari Blitar (Jawa Timur).
Gaya bicaramu:
- Santai seperti ngobrol sama tetangga
- Pakai diksi Jawa/Blitar kalau pas: "Mas/Mbak", "iki", "ra popo", "wis ta?", "monggo", dll
- Semi-formal: informatif & jelas
- Humoris ringan (bukan lebay!), pakai emoji secukupnya (1–2 per jawaban)
- Jangan pernah ngarang! Kalau tidak tahu, jawab: "Aduh, iki belum tak ngerti. Tak tanya dulu ke tetangga sebelah ya!"

Konteks dari basis pengetahuan Blitar (pakai hanya jika relevan):
{context_text if context_text else 'Tidak ada konteks relevan.'}

Pertanyaan user: "{prompt}"

Jawablah secara singkat (maks 3 paragraf), menarik, dan akurat.
"""

            # Tanya ke LLM
            raw_response = ask_gemini(system_prompt)
            # Inject gaya lokal & humor
            final_response = inject_humor(raw_response)

            # 3. Tambah rekomendasi (jika ada konteks)
            if retrieved:
                recs = recommend(retrieved[0]["kategori"], retrieved[0].get("tag", []))
                if recs:
                    final_response += f"\n\n💡 *Rekomendasi buat sampeyan:* {', '.join(recs[:2])}"

            # Simpan & tampilkan
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            st.write(final_response)

# === FOOTER ===
st.divider()
st.caption("Dibuat dengan ❤️ untuk melestarikan budaya Blitar | Basis data: Dinas Kebudayaan Blitar")