from bs4 import BeautifulSoup
import json
import re

print("Yerel dosyalardan (Wiki + Steam) başarımlar birleştiriliyor...\n")

try:
    # 1. Wiki Bilgilerini Oku
    with open("wiki.html", "r", encoding="utf-8") as f:
        wiki_soup = BeautifulSoup(f.read(), 'html.parser')

    # 2. Steam Yüzdelerini Oku
    with open("steam.html", "r", encoding="utf-8") as f:
        steam_soup = BeautifulSoup(f.read(), 'html.parser')

    # Steam yüzdelerini bir sözlüğe aktaralım (Eşleştirme kolaylığı için)
    steam_pct_map = {}
    # Steam'deki her başarım satırı 'achieveRow' class'ına sahiptir
    for row in steam_soup.find_all('div', class_='achieveRow'):
        name_div = row.find('h3')
        pct_div = row.find('span', class_='achievePercent')
        if name_div and pct_div:
            s_name = name_div.text.strip().lower()
            # Yüzde metnini float sayıya çevir (Örn: "34.2%" -> 34.2)
            pct_val = float(pct_div.text.replace('%', '').strip())
            # Harf dışı karakterleri temizleyerek güvenli anahtar oluştur
            clean_key = re.sub(r'[^a-z0-9]', '', s_name)
            steam_pct_map[clean_key] = pct_val

    achievements = []
    diff_map = {
        "very easy": "VE", "ve": "VE",
        "easy": "E", "e": "E",
        "medium": "M", "m": "M",
        "hard": "H", "h": "H",
        "very hard": "VH", "vh": "VH",
        "insane": "I", "i": "I"
    }

    # Wiki tablolarını tara
    for table in wiki_soup.find_all('table'):
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue

        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 5:
                first_cell = cols[0]
                name_div = first_cell.find('div', style=re.compile(r'bold|larger', re.I))
                desc_div = first_cell.find('div', style=re.compile(r'italic', re.I))

                if name_div:
                    name = name_div.text.replace('[edit]', '').strip()
                else:
                    name = first_cell.text.split('\n')[0].strip()

                if not name or name.lower() in ['achievement', 'name', 'başarım']:
                    continue

                desc = desc_div.text.strip() if desc_div else ""

                # Zorluk tespit et
                di = "UC"
                for col in reversed(cols):
                    col_text = col.text.strip().lower()
                    if col_text in diff_map:
                        di = diff_map[col_text]
                        break

                # ID oluştur ve Steam yüzdesiyle eşleştir
                a_id = re.sub(r'[^a-z0-9]', '', name.lower())
                if not a_id:
                    continue

                # Steam'den gelen yüzdeyi bağla, bulamazsa varsayılan 0.0 ver
                steam_pct = steam_pct_map.get(a_id, 0.0)

                if not any(a['id'] == a_id for a in achievements):
                    achievements.append({
                        "id": a_id,
                        "name": name,
                        "desc": desc,
                        "di": di,
                        "steam_pct": steam_pct,  # Yeni alan eklendi!
                        "dlc": [],
                        "ver": ""
                    })

    with open("achievements.json", "w", encoding="utf-8") as f:
        json.dump(achievements, f, ensure_ascii=False, indent=2)
    print(f"✅ Başarılı! {len(achievements)} başarım Steam yüzdeleriyle birlikte 'achievements.json'a kaydedildi.")

except FileNotFoundError as e:
    print(f"❌ Hata: Gerekli HTML dosyası eksik! {e}")