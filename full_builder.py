import json
import os
import re
from bs4 import BeautifulSoup

print("=" * 60)
print(" EU4 BAŞARIM BİRLEŞTİRİCİ VE HTML OLUŞTURUCU (v4 - Eksik Filtresi Eklendi)")
print("=" * 60)

# 1. DOSYA KONTROLLERİ
if not os.path.exists("wiki.html") or not os.path.exists("steam.html"):
    print("❌ HATA: klasörde 'wiki.html' or 'steam.html' dosyalarından biri eksik!")
    exit()

try:
    # 2. STEAM YÜZDELERİNİN AYIKLANMASI
    print("-> 'steam.html' dosyası okunuyor...")
    with open("steam.html", "r", encoding="utf-8") as f:
        steam_soup = BeautifulSoup(f.read(), 'html.parser')

    steam_pct_map = {}
    achieve_rows = steam_soup.find_all('div', class_='achieveRow')
    print(f"-> Steam dosyasında {len(achieve_rows)} adet başarım satırı bulundu.")

    for row in achieve_rows:
        name_div = row.find('h3')
        if not name_div:
            name_div = row.find('div', class_='achieveTxt')

        pct_div = row.find(class_='achievePercent')

        if name_div and pct_div:
            s_name = name_div.text.strip().lower()
            try:
                pct_val = float(pct_div.text.replace('%', '').strip())
            except:
                pct_val = 0.0

            clean_key = re.sub(r'[^a-z0-9]', '', s_name)
            if clean_key:
                steam_pct_map[clean_key] = pct_val

    print(f"✅ Steam yüzdeleri hafızaya alındı. Toplam benzersiz yüzde: {len(steam_pct_map)}")

    # 3. WIKI BİLGİLERİNİN AYIKLANMASI
    print("\n-> 'wiki.html' dosyası okunuyor...")
    with open("wiki.html", "r", encoding="utf-8") as f:
        wiki_soup = BeautifulSoup(f.read(), 'html.parser')

    achievements = []
    diff_map = {
        "very easy": "VE", "ve": "VE",
        "easy": "E", "e": "E",
        "medium": "M", "m": "M",
        "hard": "H", "h": "H",
        "very hard": "VH", "vh": "VH",
        "insane": "I", "i": "I"
    }

    tables = wiki_soup.find_all('table')
    print(f"-> Wiki dosyasında {len(tables)} adet tablo yapısı inceleniyor...")

    matched_count = 0
    for table in tables:
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

                if not name or name.lower() in ['achievement', 'name', 'başarım', 'icon']:
                    continue

                desc = desc_div.text.strip() if desc_div else ""

                # Zorluk seviyesini tespit et
                di = "UC"
                for col in reversed(cols):
                    col_text = col.text.strip().lower()
                    if col_text in diff_map:
                        di = diff_map[col_text]
                        break

                a_id = re.sub(r'[^a-z0-9]', '', name.lower())
                if not a_id:
                    continue

                steam_pct = steam_pct_map.get(a_id, 0.0)
                if steam_pct > 0:
                    matched_count += 1

                if not any(a['id'] == a_id for a in achievements):
                    achievements.append({
                        "id": a_id,
                        "name": name,
                        "desc": desc,
                        "di": di,
                        "steam_pct": steam_pct,
                        "dlc": [],
                        "ver": ""
                    })

    print(f"✅ Wiki başarımları ayıklandı. Toplam: {len(achievements)}")
    print(f"📊 Steam yüzdesiyle TAM eşleşen başarım sayısı: {matched_count}")

    with open("achievements.json", "w", encoding="utf-8") as f:
        json.dump(achievements, f, ensure_ascii=False, indent=2)

    # 4. HTML DOSYASININ BASILMASI
    data_json = json.dumps(achievements, ensure_ascii=False, separators=(",", ":"))

    TEMPLATE = r'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EU4 Başarım Defteri</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg: #e9e0c9;
    --panel: #f6f0de;
    --panel-2: #efe6cd;
    --ink: #2b2316;
    --ink-soft: #6b5f47;
    --ink-faint: #9a8d6e;
    --line: #c9b98e;
    --line-strong: #a9925f;
    --navy: #233a5e;
    --navy-deep: #182740;
    --gold: #a9791f;
    --gold-bright: #c79a30;
    --green: #3f6b3f;
    --green-bg: #e3ead9;
    --amber: #92681b;
    --amber-bg: #f1e2bd;
    --blue: #2f5d8a;
    --blue-bg: #dde7f0;
    --steam-bg: #171a21;
    --steam-text: #66c0f4;
    --shadow: 0 1px 0 rgba(43,35,22,.08), 0 6px 18px -10px rgba(43,35,22,.35);
  }
  *{box-sizing:border-box;}
  html,body{margin:0;padding:0;}
  body{
    font-family:'Inter',system-ui,sans-serif;
    color:var(--ink);
    background: radial-gradient(ellipse at top left, rgba(255,255,255,.25), transparent 60%), var(--bg);
    min-height:100vh;
  }
  .wrap{max-width:980px;margin:0 auto;padding:28px 18px 80px;}

  .ledger-head{
    background:linear-gradient(180deg, var(--navy) 0%, var(--navy-deep) 100%);
    color:#f1e9d2; border-radius:14px; padding:26px 28px 22px; box-shadow:var(--shadow);
    position:relative; overflow:hidden;
  }
  h1{ font-family:'Cinzel',serif; font-weight:700; font-size:clamp(24px,4vw,34px); margin:6px 0 4px; letter-spacing:.01em; }
  .sub{color:#cbd6e6; font-size:13.5px; margin:0 0 18px; max-width:560px; line-height:1.5;}

  .progress-row{display:flex; align-items:center; gap:16px; flex-wrap:wrap;}
  .progress-track{ flex:1 1 220px; height:10px; border-radius:6px; background:rgba(255,255,255,.14); overflow:hidden; }
  .progress-fill{height:100%; background:linear-gradient(90deg,var(--gold) 0%, var(--gold-bright) 100%); width:0%; transition:width .4s ease;}
  .progress-label{font-size:13px; color:#e9dcb8; font-weight:600; white-space:nowrap;}

  .rare-stats-box {
    margin-top: 14px; padding: 10px 14px; border-radius: 8px;
    background: rgba(0,0,0,0.25); border: 1px solid rgba(102, 192, 244, 0.4);
    font-size: 13px; color: #cbd6e6; display: none;
  }
  .rare-stats-box.show { display: inline-block; }
  .rare-stats-box b { color: var(--steam-text); }

  .toolbar{ margin-top:18px; display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
  .tabs{display:flex; flex-wrap:wrap; gap:4px; background:var(--panel-2); padding:4px; border-radius:10px; border:1px solid var(--line);}
  .tab-btn{
    border:none; background:transparent; padding:8px 14px; font-size:13.5px; font-weight:600;
    color:var(--ink-soft); border-radius:7px; cursor:pointer; display:flex; align-items:center; gap:6px;
  }
  .tab-btn.active{background:var(--navy); color:#f4ecd4; box-shadow:var(--shadow);}
  .tab-btn .count { font-size:10.5px; background:rgba(0,0,0,.08); padding:1px 6px; border-radius:8px; }

  .search-box{ position:relative; flex:1 1 200px; max-width:280px; min-width:160px; }
  .search-box input{
    width:100%; padding:9px 12px 9px 32px; border-radius:9px; border:1px solid var(--line);
    background:var(--panel); font-family:inherit; font-size:13.5px; color:var(--ink);
  }
  .search-box svg{ position:absolute; left:10px; top:50%; transform:translateY(-50%); width:14px; height:14px; color:var(--ink-faint); }

  .btn{
    font-family:inherit; font-size:13px; font-weight:600; border-radius:9px; padding:9px 13px;
    cursor:pointer; border:1px solid var(--line); background:var(--panel); color:var(--ink);
    display:inline-flex; align-items:center; gap:6px; white-space:nowrap;
  }
  .btn-sm{padding:6px 10px; font-size:12px; border-radius:7px;}
  .btn-ghost{background:transparent; border-color:transparent;}
  .btn-ghost:hover{background:var(--panel-2);}

  .filter-panel{
    margin-top:10px; padding:14px 16px; background:var(--panel); border:1px solid var(--line);
    border-radius:10px; display:none; gap:14px; flex-wrap:wrap; align-items:center;
  }
  .filter-panel.open{display:flex;}
  .filter-group{display:flex; align-items:center; gap:8px; flex-wrap:wrap;}
  .filter-label{font-size:11.5px; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-faint); font-weight:700;}
  .chip{ font-size:12px; padding:5px 11px; border-radius:20px; border:1px solid var(--line); background:var(--panel-2); cursor:pointer; font-weight:600; color:var(--ink-soft); }
  .chip.on{color:#fff; border-color:transparent;}
  select.sel{ font-family:inherit; font-size:12.5px; padding:6px 8px; border-radius:7px; border:1px solid var(--line); background:var(--panel-2); color:var(--ink); }

  .list{margin-top:16px; display:flex; flex-direction:column; gap:8px;}
  .empty-state{ text-align:center; padding:48px 20px; color:var(--ink-soft); background:var(--panel); border:1px dashed var(--line-strong); border-radius:12px; }

  /* ---------- Card Layout ---------- */
  .card{ background:var(--panel); border:1px solid var(--line); border-radius:11px; padding:13px 14px; box-shadow:var(--shadow); display:flex; gap:14px; align-items:center; }
  .card.done{opacity:.72;}
  .seal{ flex:0 0 auto; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:'Cinzel',serif; font-weight:700; font-size:11px; color:#fff; box-shadow:0 1px 3px rgba(0,0,0,.25); }
  .card-main{flex:1; min-width:0;}
  .card-top{display:flex; align-items:baseline; gap:8px; flex-wrap:wrap;}
  .a-name{font-weight:700; font-size:14.5px; color:var(--ink);}
  .a-name.done-text{text-decoration:line-through; text-decoration-color:var(--ink-faint);}
  .badge{ font-size:10px; font-weight:700; padding:2px 7px; border-radius:5px; text-transform:uppercase; }
  .a-desc{font-size:13px; color:var(--ink-soft); margin:3px 0 0; line-height:1.45;}
  .a-meta{display:flex; gap:6px; flex-wrap:wrap; margin-top:7px; align-items:center;}
  .tag{font-size:10.5px; padding:2px 7px; border-radius:5px; background:var(--panel-2); color:var(--ink-soft); border:1px solid var(--line); font-weight:600;}
  .tag.steam { background: var(--steam-bg); color: var(--steam-text); border-color: #2a475e; display:inline-flex; align-items:center; gap:4px; font-weight: 700; }
  .wiki-link{font-size:11.5px; color:var(--blue); font-weight:600; text-decoration:none; display:inline-flex; align-items:center; gap:3px;}
  .wiki-link:hover{text-decoration:underline;}

  /* ---------- Durum Seçim Grubu Tasarımı ---------- */
  .card-actions{ flex:0 0 auto; display:flex; justify-content:flex-end; }
  .status-group {
    display: flex; background: rgba(0,0,0,0.06); padding: 3px; border-radius: 8px; gap: 2px;
  }
  .status-chip {
    border: none; background: transparent; font-family: inherit; font-size: 11px; font-weight: 700;
    padding: 6px 11px; border-radius: 6px; cursor: pointer; color: var(--ink-faint);
    opacity: 0.35; transition: all 0.2s ease; white-space: nowrap;
  }
  .status-chip:hover { opacity: 0.7; background: rgba(0,0,0,0.03); }

  .status-chip.active { opacity: 1; color: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }
  .status-chip.none.active { background: var(--ink-soft); }
  .status-chip.queued.active { background: var(--amber); }
  .status-chip.inprogress.active { background: var(--blue); }
  .status-chip.done.active { background: var(--green); }

  @media (max-width: 768px){
    .card { flex-direction: column; align-items: stretch; gap: 10px; }
    .card-actions { justify-content: flex-start; margin-top: 4px; }
    .status-group { width: 100%; justify-content: space-between; }
    .status-chip { flex: 1; text-align: center; }
  }
</style>
</head>
<body>
<div class="wrap">

  <div class="ledger-head">
    <div class="eyebrow">Europa Universalis IV</div>
    <h1>Başarım Defteri</h1>
    <p class="sub">Vikiden alınan başarımları takip et, Steam nadirliğine göre süz ve sırala.</p>
    <div class="progress-row">
      <div class="progress-track"><div class="progress-fill" id="progressFill"></div></div>
      <div class="progress-label" id="progressLabel">0 / 0 tamamlandı</div>
    </div>
    <div class="rare-stats-box" id="rareStatsBox"></div>
  </div>

  <div class="toolbar">
    <div class="tabs" id="tabs">
      <button class="tab-btn" data-tab="all">Tümü <span class="count" id="cnt-all">0</span></button>
      <button class="tab-btn" data-tab="notdone">Tamamlanmayan <span class="count" id="cnt-notdone">0</span></button>
      <button class="tab-btn" data-tab="queue">Sıra <span class="count" id="cnt-queue">0</span></button>
      <button class="tab-btn" data-tab="done">Tamamlanan <span class="count" id="cnt-done">0</span></button>
    </div>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="Başarım ara…">
    </div>
    <button class="btn" id="filterToggle">Süz / Sırala</button>
  </div>

  <div class="filter-panel" id="filterPanel">
    <div class="filter-group">
      <span class="filter-label">Zorluk</span>
      <span class="chip" data-di="VE">Çok Kolay</span>
      <span class="chip" data-di="E">Kolay</span>
      <span class="chip" data-di="M">Orta</span>
      <span class="chip" data-di="H">Zor</span>
      <span class="chip" data-di="VH">Çok Zor</span>
      <span class="chip" data-di="I">İmkansız Gibi</span>
    </div>
    <div class="filter-group">
      <span class="filter-label">Sırala</span>
      <select class="sel" id="sortSelect">
        <option value="alpha">İsme Göre (A-Z)</option>
        <option value="steam_rare">Steam Nadirliğine Göre (En Nadir ↑)</option>
        <option value="steam_common">Steam Popülerliğine Göre (En Yaygın ↓)</option>
        <option value="diff">Zorluğa Göre (Kolay → Zor)</option>
        <option value="diffdesc">Zorluğa Göre (Zor → Kolay)</option>
      </select>
    </div>
    <button class="btn btn-sm btn-ghost" id="clearFilters">Temizle</button>
  </div>

  <div class="list" id="listArea"></div>
</div>

<script>
const BASE_ACHIEVEMENTS = __ACHIEVEMENTS_JSON__;

const DI_COLOR = { VE:'#5f8c52', E:'#3f7a63', M:'#a9791f', H:'#b5481f', VH:'#7a2030', I:'#3d2645', UC:'#8a8270' };
const DI_LABEL = { VE:'Çok Kolay', E:'Kolay', M:'Orta', H:'Zor', VH:'Çok Zor', I:'İmkansız Gibi', UC:'Bilinmiyor' };
const DI_ORDER = { VE:0, E:1, M:2, H:3, VH:4, I:5, UC:6 };

let state = { statuses:{} };
const STORAGE_KEY = 'eu4-tracker-state-v1';

try{
  const saved = localStorage.getItem(STORAGE_KEY);
  if(saved) state = JSON.parse(saved);
}catch(e){}

function saveState(){ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }

function setStatus(id, newStatus){
  if(newStatus === 'none') {
    delete state.statuses[id];
  } else {
    state.statuses[id] = newStatus;
  }
  saveState();
  render();
}

let activeTab = 'all'; let search = ''; let activeDi = new Set(); let sortMode = 'alpha';

function sortList(list){
  const arr = list.slice();
  if(sortMode==='alpha') arr.sort((a,b)=>a.name.localeCompare(b.name));
  else if(sortMode==='diff') arr.sort((a,b)=>(DI_ORDER[a.di]??9)-(DI_ORDER[b.di]??9) || a.name.localeCompare(b.name));
  else if(sortMode==='diffdesc') arr.sort((a,b)=>(DI_ORDER[b.di]??9)-(DI_ORDER[a.di]??9) || a.name.localeCompare(b.name));
  else if(sortMode==='steam_rare') arr.sort((a,b)=>(a.steam_pct ?? 100) - (b.steam_pct ?? 100));
  else if(sortMode==='steam_common') arr.sort((a,b)=>(b.steam_pct ?? 0) - (a.steam_pct ?? 0));
  return arr;
}

function cardHtml(a){
  const cur = state.statuses[a.id] || 'none';
  const isDone = cur==='done';
  const wikiUrl = 'https://eu4.paradoxwikis.com/index.php?search=' + encodeURIComponent(a.name);

  let pctDisplay = a.steam_pct > 0 ? `%${a.steam_pct}` : '%0.0';
  let steamTag = `<span class="tag steam">🎮 Steam Oranı: ${pctDisplay}</span>`;

  return `
  <div class="card ${isDone?'done':''}">
    <div class="seal" style="background:${DI_COLOR[a.di]||'#888'}">${a.di||'?'}</div>
    <div class="card-main">
      <div class="card-top">
        <span class="a-name ${isDone?'done-text':''}">${a.name}</span>
        <span class="badge" style="background:${DI_COLOR[a.di]}22;color:${DI_COLOR[a.di]}">${DI_LABEL[a.di]||a.di}</span>
      </div>
      <p class="a-desc">${a.desc || 'Açıklama bulunamadı.'}</p>
      <div class="a-meta">
        ${steamTag}
        <a class="wiki-link" href="${wikiUrl}" target="_blank" rel="noopener">Vikide Aç ↗</a>
      </div>
    </div>
    <div class="card-actions">
      <div class="status-group">
        <button class="status-chip none ${cur==='none'?'active':''}" onclick="setStatus('${a.id}', 'none')">Başlanmadı</button>
        <button class="status-chip queued ${cur==='queued'?'active':''}" onclick="setStatus('${a.id}', 'queued')">Sırada</button>
        <button class="status-chip inprogress ${cur==='inprogress'?'active':''}" onclick="setStatus('${a.id}', 'inprogress')">Yapılıyor</button>
        <button class="status-chip done ${cur==='done'?'active':''}" onclick="setStatus('${a.id}', 'done')">Tamamlandı</button>
      </div>
    </div>
  </div>`;
}

function render(){
  const all = BASE_ACHIEVEMENTS;
  const total = all.length;
  const doneAchievements = all.filter(a => state.statuses[a.id]==='done');
  const doneCount = doneAchievements.length;
  const notDoneCount = total - doneCount;
  const progCount = all.filter(a => state.statuses[a.id]==='inprogress').length;
  const queuedCount = all.filter(a => state.statuses[a.id]==='queued').length;

  document.getElementById('progressFill').style.width = total ? (doneCount/total*100)+'%' : '0%';
  document.getElementById('progressLabel').textContent = doneCount+' / '+total+' tamamlandı';
  document.getElementById('cnt-all').textContent = total;
  document.getElementById('cnt-notdone').textContent = notDoneCount;
  document.getElementById('cnt-queue').textContent = queuedCount+progCount;
  document.getElementById('cnt-done').textContent = doneCount;

  const rareBox = document.getElementById('rareStatsBox');
  const validDone = doneAchievements.filter(a => a.steam_pct > 0);
  if(validDone.length > 0){
    validDone.sort((a,b) => a.steam_pct - b.steam_pct);
    rareBox.innerHTML = `🏆 Açtığınız En Nadir Başarım: <b>${validDone[0].name}</b> (Dünyada sadece <b>%${validDone[0].steam_pct}</b> kişide var)`;
    rareBox.classList.add('show');
  } else { rareBox.classList.remove('show'); }

  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active', b.dataset.tab===activeTab));

  let list = all;
  if(search.trim()){
    const q = search.trim().toLowerCase();
    list = list.filter(a => a.name.toLowerCase().includes(q) || (a.desc||'').toLowerCase().includes(q));
  }
  if(activeDi.size) list = list.filter(a => activeDi.has(a.di));

  if(activeTab==='notdone') list = list.filter(a=>state.statuses[a.id]!=='done');
  else if(activeTab==='queue') list = list.filter(a=>['queued','inprogress'].includes(state.statuses[a.id]));
  else if(activeTab==='done') list = list.filter(a=>state.statuses[a.id]==='done');

  list = sortList(list);

  const listArea = document.getElementById('listArea');
  if(list.length===0){
    listArea.innerHTML = '<div class="empty-state">Eşleşen başarım bulunamadı.</div>';
  } else {
    listArea.innerHTML = list.map(a => cardHtml(a)).join('');
  }
}

document.getElementById('tabs').addEventListener('click', e=>{
  const btn = e.target.closest('.tab-btn'); if(btn){ activeTab = btn.dataset.tab; render(); }
});
document.getElementById('searchInput').addEventListener('input', e=>{ search = e.target.value; render(); });
document.getElementById('filterToggle').addEventListener('click', ()=>document.getElementById('filterPanel').classList.toggle('open'));
document.getElementById('sortSelect').addEventListener('change', e=>{ sortMode = e.target.value; render(); });
document.getElementById('clearFilters').addEventListener('click', ()=>{
  search=''; document.getElementById('searchInput').value=''; activeDi.clear();
  document.querySelectorAll('.chip[data-di]').forEach(c=>{c.classList.remove('on'); c.style.background=''; c.style.color='';});
  sortMode='alpha'; document.getElementById('sortSelect').value='alpha'; render();
});
document.querySelectorAll('.chip[data-di]').forEach(chip=>{
  chip.addEventListener('click', ()=>{
    const di = chip.dataset.di;
    if(activeDi.has(di)){ activeDi.delete(di); chip.classList.remove('on'); chip.style.background=''; chip.style.color=''; }
    else { activeDi.add(di); chip.classList.add('on'); chip.style.background = DI_COLOR[di]; chip.style.color='#fff'; }
    render();
  });
});

render();
</script>
</body>
</html>'''

    html = TEMPLATE.replace("__ACHIEVEMENTS_JSON__", data_json)
    with open("eu4_achievement_tracker_steam.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\n" + "=" * 60)
    print(" 🎉 MÜKEMMEL! 'eu4_achievement_tracker_steam.html' BAŞARIYLA GÜNCELLENDİ!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Çalışma zamanı hatası: {e}")