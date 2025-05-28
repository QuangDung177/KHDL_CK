from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import os
import time
from PIL import Image
from io import BytesIO

# Từ khóa cho mỗi loài (tên Việt + tiếng Anh + tiếng Hindi + tên khoa học + tiếng Ấn)
keywords = {
    "du_du": ["lá đu đủ", "papaya leaf", "पपीता पत्ता", "Carica papaya leaf", "பப்பாளி இலை"],
    "la_sa": ["lá sả", "lemongrass leaf", "नींबू घास पत्ता", "Cymbopogon leaf", "எலுமிச்சை புல் இலை"],
    "tao_ta": ["lá táo ta", "vietnam apple leaf", "वियतनाम सेब के पत्ते", "Malus doumeri leaf", "வியட்நாம் ஆப்பிள் இலை"],
    "rau_ma": ["lá rau má", "pennywort leaf", "थानकुनी पत्ता", "Centella asiatica leaf", "வல்லாரை இலை"],
    "ngo_ri": ["ngò rí", "coriander leaf", "धनिया पत्ता", "Coriandrum sativum leaf", "கொத்தமல்லி இலை"],
    "bac_ha": ["lá bạc hà", "mint leaf", "पुदीने के पत्ते", "Mentha leaf", "புதினா இலை"],
    "tra_xanh": ["lá trà xanh", "green tea leaf", "हरी चाय पत्ती", "Camellia sinensis leaf", "பச்சை தேயிலை இலை"]
}

# Thiết lập trình duyệt
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Tải ảnh từ từng từ khóa
for folder, terms in keywords.items():
    os.makedirs(folder, exist_ok=True)
    for term in terms:
        print(f"Đang tìm: {term}")
        
        # Đếm số lượng ảnh đã có để tiếp tục đếm
        existing_images = [f for f in os.listdir(folder) if f.startswith(term.replace(' ', '_')) and f.endswith('.jpg')]
        count = len(existing_images)
        print(f"Đã có {count} ảnh, tiếp tục tải thêm...")
        
        url = f"https://www.google.com/search?q={term}&tbm=isch"
        driver.get(url)
        time.sleep(2)

        # Cuộn trang để load thêm ảnh
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(1)

        # Parse HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        images = soup.find_all("img")
        for img in images:
            try:
                src = img.get("src")
                if not src or "http" not in src:
                    continue
                response = requests.get(src, timeout=5)
                image = Image.open(BytesIO(response.content))
                if image.width < 180 or image.height < 180:
                    continue
                image = image.resize((640, 640))
                filename = os.path.join(folder, f"{term.replace(' ', '_')}_{count}.jpg")
                image.save(filename)
                count += 1
                if count >= 1000:  # tăng tối đa lên 1000 ảnh mỗi từ khóa
                    break
            except:
                continue

driver.quit()
print("Đã tải và resize xong.")