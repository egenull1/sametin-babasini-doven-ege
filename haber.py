import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import traceback

# --- E-POSTA AYARLARI ---
# Bu kısmı kendi e-posta bilgilerinizle doldurun.
# Gmail kullanıyorsanız, hesabınızda "Uygulama Şifresi" oluşturmanız ve onu kullanmanız gerekir.
SMTP_SERVER = "mail.kiyaslasana.com"  # SMTP sunucunuz (Örn: smtp.gmail.com)
SMTP_PORT = 587  # TLS için genellikle 587
EMAIL_ADRESINIZ = "samet@kiyaslasana.com"  # Gönderici e-posta adresi
EMAIL_SIFRENIZ = "Galatasaray1!"  # E-posta uygulama şifreniz
ALICI_EMAIL_ADRESI = "sametbeyiniz61@gmail.com"  # Haberlerin gönderileceği e-posta adresi


def json_dosyasini_oku(dosya_yolu):
    """Belirtilen yoldaki JSON dosyasını okur ve içeriğini döndürür."""
    if os.path.exists(dosya_yolu):
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] # Bozuk JSON dosyası varsa boş liste döndür
    return []

def json_dosyasina_yaz(dosya_yolu, veri):
    """Verilen veriyi belirtilen yoldaki JSON dosyasına yazar."""
    with open(dosya_yolu, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

def mail_gonder(icerik):
    """Hazırlanan içeriği e-posta olarak gönderir."""
    if not all([SMTP_SERVER, EMAIL_ADRESINIZ, EMAIL_SIFRENIZ, ALICI_EMAIL_ADRESI]) or "ornek@gmail.com" in EMAIL_ADRESINIZ:
        print("\n--- E-POSTA GÖNDERİMİ ATLANDI ---")
        print("Lütfen script'in başındaki SMTP_SERVER, EMAIL_ADRESINIZ, EMAIL_SIFRENIZ ve ALICI_EMAIL_ADRESI alanlarını doldurun.")
        return
        
    try:
        msg = MIMEText(icerik, 'plain', 'utf-8')
        msg['Subject'] = Header('Yeni Teknoloji Haberleri Bulundu!', 'utf-8')
        msg['From'] = EMAIL_ADRESINIZ
        msg['To'] = ALICI_EMAIL_ADRESI

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADRESINIZ, EMAIL_SIFRENIZ)
        server.sendmail(EMAIL_ADRESINIZ, [ALICI_EMAIL_ADRESI], msg.as_string())
        server.quit()
        print("E-posta başarıyla gönderildi.")
    except Exception as e:
        print(f"E-posta gönderilirken bir hata oluştu: {e}")

# --- WEB SİTESİ KONTROL FONKSİYONLARI ---

def webtekno_kontrol_et():
    """Webtekno'daki yeni haberleri kontrol eder."""
    site_adi = "Webtekno"
    url = "https://www.webtekno.com/"
    json_dosyasi = "webtekno_haberler.json"
    
    print(f"{site_adi} kontrol ediliyor...")
    yeni_haberler, mevcut_haberler = [], []
    eski_haber_linkleri = [haber['link'] for haber in json_dosyasini_oku(json_dosyasi)]
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            haber_listesi = soup.find_all('div', class_='content-timeline__item', limit=10)
            for haber_blogu in haber_listesi:
                baslik_elementi = haber_blogu.find('h3', class_='content-timeline__detail__title')
                link_elementi = haber_blogu.find('div', class_='content-timeline__media').find('a')
                if baslik_elementi and link_elementi and 'href' in link_elementi.attrs:
                    baslik = baslik_elementi.get_text(strip=True)
                    link = link_elementi['href']
                    if not link.startswith('http'):
                        link = url.rstrip('/') + (link if link.startswith('/') else '/' + link)
                    mevcut_haberler.append({'baslik': baslik, 'link': link})
        else:
            print(f"{site_adi} sitesine ulaşılamadı. Durum Kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{site_adi} sitesine bağlanırken bir hata oluştu: {e}")

    if mevcut_haberler:
        for haber in mevcut_haberler:
            if haber['link'] not in eski_haber_linkleri:
                yeni_haberler.append(haber)
        # --- DÜZELTME: Çekilen tüm haberleri kaydet ---
        json_dosyasina_yaz(json_dosyasi, mevcut_haberler)
    else:
        print(f"{site_adi} için haberler bulunamadı. Site yapısı değişmiş olabilir.")

    if yeni_haberler:
        print(f"-> {site_adi} kontrolü tamamlandı. {len(yeni_haberler)} yeni haber bulundu.")
    else:
        print(f"-> {site_adi} kontrolü tamamlandı. Yeni haber bulunamadı.")
    return site_adi, yeni_haberler


def shiftdelete_kontrol_et():
    """Shiftdelete.net'teki yeni haberleri kontrol eder."""
    site_adi = "ShiftDelete.Net"
    url = "https://shiftdelete.net/haberler"
    json_dosyasi = "shiftdelete_haberler.json"
    
    print(f"{site_adi} kontrol ediliyor...")
    yeni_haberler, mevcut_haberler = [], []
    eski_haber_linkleri = [haber['link'] for haber in json_dosyasini_oku(json_dosyasi)]
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            haber_bloglari = soup.select('div.tdb_module_loop.td_module_wrap', limit=10)
            for haber_blogu in haber_bloglari:
                h3_etiketi = haber_blogu.find('h3', class_='entry-title td-module-title')
                if h3_etiketi and (a_etiketi := h3_etiketi.find('a')) and 'href' in a_etiketi.attrs:
                    mevcut_haberler.append({'baslik': a_etiketi.get_text(strip=True), 'link': a_etiketi['href']})
        else:
            print(f"{site_adi} sitesine ulaşılamadı. Durum Kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{site_adi} sitesine bağlanırken bir hata oluştu: {e}")

    if mevcut_haberler:
        for haber in mevcut_haberler:
            if haber['link'] not in eski_haber_linkleri:
                yeni_haberler.append(haber)
        # --- DÜZELTME: Çekilen tüm haberleri kaydet ---
        json_dosyasina_yaz(json_dosyasi, mevcut_haberler)
    else:
        print(f"{site_adi} için haberler bulunamadı. Site yapısı değişmiş olabilir.")

    if yeni_haberler:
        print(f"-> {site_adi} kontrolü tamamlandı. {len(yeni_haberler)} yeni haber bulundu.")
    else:
        print(f"-> {site_adi} kontrolü tamamlandı. Yeni haber bulunamadı.")
    return site_adi, yeni_haberler

def donanimhaber_kontrol_et():
    """donanimhaber.com'daki yeni haberleri kontrol eder."""
    site_adi = "DonanımHaber"
    url = "https://www.donanimhaber.com/"
    json_dosyasi = "donanimhaber_haberler.json"

    print(f"{site_adi} kontrol ediliyor...")
    yeni_haberler, mevcut_haberler = [], []
    eski_haber_linkleri = [haber['link'] for haber in json_dosyasini_oku(json_dosyasi)]
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            haber_bloglari = soup.find_all('article', class_='medya', limit=10)
            for haber_blogu in haber_bloglari:
                govde = haber_blogu.find('div', class_='govde')
                if govde and (a_etiketi := govde.find('a', class_='baslik')) and a_etiketi.has_attr('href'):
                    baslik = a_etiketi.get('data-title', a_etiketi.get_text(strip=True))
                    link = url.rstrip('/') + a_etiketi['href']
                    mevcut_haberler.append({'baslik': baslik, 'link': link})
        else:
            print(f"{site_adi} sitesine ulaşılamadı. Durum Kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{site_adi} sitesine bağlanırken bir hata oluştu: {e}")

    if mevcut_haberler:
        for haber in mevcut_haberler:
            if haber['link'] not in eski_haber_linkleri:
                yeni_haberler.append(haber)
        # --- DÜZELTME: Çekilen tüm haberleri kaydet ---
        json_dosyasina_yaz(json_dosyasi, mevcut_haberler)
    else:
        print(f"{site_adi} için haberler bulunamadı. Site yapısı değişmiş olabilir.")
    
    if yeni_haberler:
        print(f"-> {site_adi} kontrolü tamamlandı. {len(yeni_haberler)} yeni haber bulundu.")
    else:
        print(f"-> {site_adi} kontrolü tamamlandı. Yeni haber bulunamadı.")
    return site_adi, yeni_haberler

def donanimarsivi_kontrol_et():
    """donanimarsivi.com'daki yeni haberleri kontrol eder."""
    site_adi = "Donanım Arşivi"
    url = "https://donanimarsivi.com/"
    json_dosyasi = "donanimarsivi_haberler.json"
    
    print(f"{site_adi} kontrol ediliyor...")
    yeni_haberler, mevcut_haberler = [], []
    eski_haber_linkleri = [haber['link'] for haber in json_dosyasini_oku(json_dosyasi)]

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            haber_bloglari = soup.find_all('article', class_='zox-art-wrap', limit=10)
            for haber_blogu in haber_bloglari:
                title_div = haber_blogu.find('div', class_='zox-art-title')
                if title_div and (a_etiketi := title_div.find('a')) and 'href' in a_etiketi.attrs:
                    if h2_etiketi := a_etiketi.find('h2'):
                        baslik = h2_etiketi.get_text(strip=True)
                        link = a_etiketi['href']
                        mevcut_haberler.append({'baslik': baslik, 'link': link})
        else:
            print(f"{site_adi} sitesine ulaşılamadı. Durum Kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{site_adi} sitesine bağlanırken bir hata oluştu: {e}")

    if mevcut_haberler:
        for haber in mevcut_haberler:
            if haber['link'] not in eski_haber_linkleri:
                yeni_haberler.append(haber)
        # --- DÜZELTME: Çekilen tüm haberleri kaydet ---
        json_dosyasina_yaz(json_dosyasi, mevcut_haberler)
    else:
        print(f"{site_adi} için haberler bulunamadı. Site yapısı değişmiş olabilir.")

    if yeni_haberler:
        print(f"-> {site_adi} kontrolü tamamlandı. {len(yeni_haberler)} yeni haber bulundu.")
    else:
        print(f"-> {site_adi} kontrolü tamamlandı. Yeni haber bulunamadı.")
    return site_adi, yeni_haberler

def ntv_kontrol_et():
    """ntv.com.tr'deki yeni haberleri kontrol eder."""
    site_adi = "NTV"
    url_base = "https://www.ntv.com.tr"
    url_path = "/teknoloji"
    json_dosyasi = "ntv_haberler.json"
    
    print(f"{site_adi} kontrol ediliyor...")
    yeni_haberler, mevcut_haberler = [], []
    eski_haber_linkleri = [haber['link'] for haber in json_dosyasini_oku(json_dosyasi)]

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        response = requests.get(url_base + url_path, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            haber_bloglari = soup.find_all('div', class_='card card--md', limit=10)
            for haber_blogu in haber_bloglari:
                h3_etiketi = haber_blogu.find('h3', class_='card-text')
                if h3_etiketi and (a_etiketi := h3_etiketi.find('a')) and 'href' in a_etiketi.attrs:
                    baslik = a_etiketi.get_text(strip=True)
                    link = url_base + a_etiketi['href']
                    mevcut_haberler.append({'baslik': baslik, 'link': link})
        else:
            print(f"{site_adi} sitesine ulaşılamadı. Durum Kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{site_adi} sitesine bağlanırken bir hata oluştu: {e}")

    if mevcut_haberler:
        for haber in mevcut_haberler:
            if haber['link'] not in eski_haber_linkleri:
                yeni_haberler.append(haber)
        # --- DÜZELTME: Çekilen tüm haberleri kaydet ---
        json_dosyasina_yaz(json_dosyasi, mevcut_haberler)
    else:
        print(f"{site_adi} için haberler bulunamadı. Site yapısı değişmiş olabilir.")

    if yeni_haberler:
        print(f"-> {site_adi} kontrolü tamamlandı. {len(yeni_haberler)} yeni haber bulundu.")
    else:
        print(f"-> {site_adi} kontrolü tamamlandı. Yeni haber bulunamadı.")
    return site_adi, yeni_haberler

# --- ANA KOD ---
if __name__ == "__main__":
    print("Haber kontrol süreci başlatıldı.")
    tum_yeni_haberler = {}
    
    kontrol_fonksiyonlari = [
        webtekno_kontrol_et,
        shiftdelete_kontrol_et,
        donanimhaber_kontrol_et,
        donanimarsivi_kontrol_et,
        ntv_kontrol_et
    ]
    
    for fonksiyon in kontrol_fonksiyonlari:
        try:
            site_adi, yeni_haberler = fonksiyon()
            if yeni_haberler:
                tum_yeni_haberler[site_adi] = yeni_haberler
        except Exception as e:
            print(f"'{getattr(fonksiyon, '__name__', 'Bilinmeyen fonksiyon')}' çalıştırılırken bir hata oluştu: {e}")
            traceback.print_exc()

    print("\n" + "="*40)
    if tum_yeni_haberler:
        mail_icerigi = "Sitelerde yeni haberler bulundu:\n\n"
        for site, haberler in tum_yeni_haberler.items():
            mail_icerigi += f"--- {site} ({len(haberler)} Yeni Haber) ---\n"
            for i, haber in enumerate(reversed(haberler), 1):
                mail_icerigi += f"{i}. {haber['baslik']}\n   Link: {haber['link']}\n"
            mail_icerigi += "\n"
            
        print("\n--- Gönderilecek Mail İçeriği ---\n")
        print(mail_icerigi)
        print("---------------------------------")
        mail_gonder(mail_icerigi)
    else:
        print("\nTüm siteler kontrol edildi. Yeni bir haber bulunamadı.")
    
    print("\n" + "="*40)
    print("Haber kontrol süreci tamamlandı.")
