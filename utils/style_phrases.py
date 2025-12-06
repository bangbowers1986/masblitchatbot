# utils/style_phrases.py
import random

HUMOR_OPENERS = [
    "Wah, sampeyan nanya iki? Monggo, tak critakno…",
    "Oalah, iki favoritku! 😄",
    "Hati-hati, nanti ketagihan!",
    "Siap-siap ngiler, ya…",
    "Aduh, iki cerita legendaris Blitar!",
    "Jangan kaget, lho—iki fakta beneran!",
]

HUMOR_CLOSERS = [
    "Gimana? Mau coba? 😋",
    "Ra popo kalau keringetan—wong enak tenan!",
    "Kalau ke Blitar, jangan lupa selfie di sini, ya! 📸",
    "Wis ta? Ayo, tak anterin ke lokasi!",
    "Kalau belum cobain, belum sah jadi wong Blitar!",
    "Mbak/Mas, kapan main ke Blitar? Tak traktir pecel!",
]

LOCAL_PHRASES = {
    "iya": ["iki", "iya", "monggo", "wis", "siap"],
    "tidak": ["mboten", "ra", "ora", "belum"],
    "enak": ["enak tenan", "maknyus", "nendang", "jos", "gurih pol"],
    "rekomendasi": ["coba ae", "wajib", "jangan sampe kelewatan", "jangan nyesel"]
}

def inject_humor(text: str) -> str:
    """Tambahkan frase humor & lokal secara alami."""
    if not text.strip():
        return text

    lines = text.split('\n')
    # Tambah di awal & akhir
    if random.random() < 0.7:
        opener = random.choice(HUMOR_OPENERS)
        lines = [opener] + lines
    if random.random() < 0.6 and len(lines) > 1:
        closer = random.choice(HUMOR_CLOSERS)
        lines.append("")
        lines.append(closer)

    return "\n".join(lines)