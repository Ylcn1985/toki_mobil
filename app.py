import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import urllib3

# 1. SAYFA AYARLARI
st.set_page_config(page_title="TOKİ Mobil", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stHorizontalBlock"] { gap: 1px !important; }
    [data-testid="column"] { padding: 0px !important; }
    div.stButton > button {
        width: 100%; border-radius: 0px; background-color: white;
        color: #2c3e50; border: 0.5px solid #ddd; padding: 2px 0px;
        font-size: 10px !important; font-weight: 700; height: 28px;
    }
    .ihale-kart {
        background-color: white; border-radius: 8px; padding: 12px;
        margin-bottom: 8px; border-left: 8px solid #347083;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .ihale-tarih { color: #d35400; font-weight: 900; font-size: 18px; display: block; }
    .ihale-is { color: #333; font-size: 14px; font-weight: 600; }
    .block-container { padding: 5px !important; }
    footer, #MainMenu, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 3. VERİ ÇEKME
@st.cache_data(ttl=600)
def veri_getir():
    try:
        url = "https://www.toki.gov.tr/ihale-tarihleri"
        res = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table: return []
        
        items = []
        for row in table.find_all('tr')[1:]:
            tds = row.find_all('td')
            if len(tds) >= 4:
                txt = tds[1].text.strip()
                match = re.search(r"([A-ZÇĞİÖŞÜa-zçğıöşü]+)\s+İli", txt)
                il_adi = match.group(1).upper() if match else "DİĞER"
                items.append({"il": il_adi, "is": txt, "zaman": tds[3].text.strip()})
        return items
    except:
        return []

# 4. GÖRÜNÜM
data = veri_getir()

st.write("### 📍 TOKİ İhale Takip")

if not data:
    st.warning("Veriler yükleniyor veya şu an TOKİ sitesine ulaşılamıyor. Lütfen sayfayı yenileyin.")
else:
    # Filtreleme
    iller = sorted(list(set(d['il'] for d in data)))
    
    # Tümünü göster
    if st.button("🌍 TÜMÜ"):
        st.session_state['filtre'] = "ALL"
    
    # İller (5'li Bitişik)
    cols = st.columns(5)
    for i, il in enumerate(iller):
        with cols[i % 5]:
            if st.button(il, key=il):
                st.session_state['filtre'] = il

    st.markdown("---")
    
    secili_il = st.session_state.get('filtre', 'ALL')
    sonuclar = data if secili_il == "ALL" else [d for d in data if d['il'] == secili_il]

    for s in sonuclar:
        st.markdown(f"""
            <div class="ihale-kart">
                <span class="ihale-tarih">🗓 {s['zaman']}</span>
                <div class="ihale-is">{s['is']}</div>
            </div>
        """, unsafe_allow_html=True)