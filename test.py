from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import os
import cv2
from selenium.webdriver.common.by import By
from multiprocessing import Process

LEFT_TOLBAR_XPATH = '/html/body/div[1]/div/div/div[3]/div/header/div/div[1]'

def is_user_logged_in(driver):
    try:
        driver.find_element(by=By.XPATH, value=LEFT_TOLBAR_XPATH)
        return True
    except:
        return False
    

def capture_qr(driver, qr_path_cropped):
    try:
        qr_element = driver.find_element("css selector", "canvas")
        location = qr_element.location
        size = qr_element.size

        full_path = qr_path_cropped.replace("Crop_qrcodes", "qrcodes")
        driver.save_screenshot(full_path)
        image = cv2.imread(full_path)

        left = int(location['x'])
        top = int(location['y'])
        right = left + int(size['width'])
        bottom = top + int(size['height'])

        qr_image = image[top:bottom, left:right]
        cv2.imwrite(qr_path_cropped, qr_image)
        os.remove(full_path)

        print("✅ QR ذخیره شد:", qr_path_cropped)
    except Exception as e:
        print("⚠️ خطا در ذخیره QR:", e)

def start_whatsapp_session(user_id):
    session_dir = f"sessions/user_{user_id}"
    qr_path_cropped = f"media/Crop_qrcodes/user_{user_id}.png"

    os.makedirs('media/Crop_qrcodes', exist_ok=True)
    os.makedirs("media/qrcodes", exist_ok=True)
    os.makedirs(session_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={os.path.abspath(session_dir)}")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")  # Optional
    # chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://web.whatsapp.com/")
    time.sleep(10)

    start_time = time.time()
    while time.time() - start_time < 60:
        if is_user_logged_in(driver):
            print(f"🎉 کاربر {user_id} لاگین شد.")
            driver.quit()
            return

        capture_qr(driver, qr_path_cropped)
        time.sleep(15)

    print(f"⌛ کاربر {user_id} لاگین نشد.")
    driver.quit()


if __name__ == '__main__':
    # Start 5 concurrent WhatsApp sessions
    processes = []

    for user_id in range(1, 6):  # Users 1 to 5
        p = Process(target=start_whatsapp_session, args=(user_id,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("📌 همه سشن‌ها پایان یافتند.")
