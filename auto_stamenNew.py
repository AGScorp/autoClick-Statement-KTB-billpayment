from playwright.sync_api import Playwright, sync_playwright, expect
import os
import zipfile
import csv

        
def format_number(number):
    str_number = str(number)
    
    if len(str_number) < 4:
        return str_number
    else:
        # นำตัวเลขที่อยู่ในตำแหน่งแรกมาต่อหลัง
        formatted_number = str_number[:-3] + '-' + str_number[-3:]
        return formatted_number[-5:]


def run(playwright: Playwright, username: str, password: str, client_code: str, Account_No: str) -> None:
    # ใช้พารามิเตอร์ที่ส่งเข้ามา
    idCode = Account_No
    company_ID = client_code

     
    # เปิด browser แบบแสดงหน้าต่าง
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--start-maximized"
        ]
    )
    context = browser.new_context()
    page = context.new_page()

    print("🌐 กำลังเปิดหน้าเว็บ Krungthai Corporate Online...")
    page.goto("https://www.bizgrowing.krungthai.com/corporate/Login.do?cmd=init")
    print("✅ เปิดหน้าเว็บสำเร็จ")



    # คลิกและกรอกข้อมูลในช่อง Company ID
    page.get_by_role("row", name="Company ID", exact=True).get_by_role("textbox").click()
    page.get_by_role("row", name="Company ID", exact=True).get_by_role("textbox").fill(company_ID)

    # คลิกและกรอกข้อมูลในช่อง User ID
    page.get_by_role("row", name="User ID", exact=True).get_by_role("textbox").click()
    page.get_by_role("row", name="User ID", exact=True).get_by_role("textbox").fill(username)

    # คลิกและกรอกข้อมูลในช่อง Password (ใช้ locator ตาม id ของฟิลด์)
    page.locator("#password-field").click()
    page.locator("#password-field").fill(password)

    # คลิกปุ่ม Login เพื่อเข้าสู่ระบบ
    page.get_by_role("button", name="Login").click()

    # คลิกลิงก์ "Download" อันแรกที่พบในหน้า (กรณีมีหลายลิงก์)
    page.get_by_role("link", name="Download").first.click()

    

# #เลือกวันที่
    # page.get_by_role("cell", name="Krungthai Corporate Online :").locator("img").nth(2).click()
    # page.get_by_role("link", name="1", exact=True).click()





    # page.pause() # รอให้หน้าโหลดเสร็จ //////////


    # เลือกบัญชี - ใช้ mapping เพื่อเลือกบัญชีที่ถูกต้อง
    # สร้าง mapping ของ Account_No กับค่าที่ต้องเลือกใน dropdown
    account_mapping = {
        "2716007306": "6102",
        "2926010214": "6945",
        "4126048820": "6946"
    }

    # ตรวจสอบว่า idCode นี้อยู่ใน mapping หรือไม่
    if idCode in account_mapping:
        dropdown_value = account_mapping[idCode]

        # คลิกเลือก dropdown
        page.get_by_role("cell", name="Krungthai Corporate Online :").get_by_role("list").click()

        # คลิกเลือกค่าที่ตรงกับ idCode
        page.locator("#select2-drop").get_by_text(dropdown_value).click()
    else:
        print(f"ไม่พบ Account_No: {idCode} ใน mapping")
        # ใช้ค่าเริ่มต้น
        page.get_by_role("cell", name="Krungthai Corporate Online :").get_by_role("list").click()
        page.locator("#select2-drop").get_by_text("6946").click()




# เลือกปุ่ม ค้นหา
    page.get_by_role("button", name="Search").click()
    page.locator("input[name=\"ch_comcodeAll\"]").check()

    # page.pause() # รอให้หน้าโหลดเสร็จ //////////

 

    logged_out = False

    try:
        # --- ตรวจสอบว่ามีปุ่ม Download หรือไม่ ---
        download_button = page.get_by_role("button", name="Download")

        # รอปุ่ม Download ให้ปรากฏ (timeout 10 วินาที)
        download_button.wait_for(state="visible", timeout=15)

        # --- คลิกปุ่มดาวน์โหลด ---
        download_button.click()

        # --- รอให้การดาวน์โหลดเกิดขึ้น ---
        with page.expect_download() as download_info:
            page.get_by_label("", exact=True).get_by_role("button", name="Download").click()

        # ได้อ็อบเจกต์ของไฟล์ที่ดาวน์โหลด
        download = download_info.value

        # ดูชื่อไฟล์จริงที่ถูกดาวน์โหลด
        original_filename = download.suggested_filename
        print(f"📎 ไฟล์ที่ดาวน์โหลดชื่อเดิม: {original_filename}")

        # --- เตรียม path สำหรับบันทึกไฟล์ ---
        download_path = os.path.join(os.getcwd(), "Doc_downloads")
        os.makedirs(download_path, exist_ok=True)

        # --- กำหนดชื่อไฟล์ที่ใช้บันทึก ---
        file_ext = os.path.splitext(original_filename)[1]  # เช่น ".zip"
        download_file_name = f"{idCode}{file_ext}"         # เช่น 123456.zip
        download_file_path = os.path.join(download_path, download_file_name)

        # --- บันทึกไฟล์ลงในโฟลเดอร์ ---
        download.save_as(download_file_path)
        print(f"✅ ไฟล์ถูกบันทึกไว้ที่: {download_file_path}")

        # --- ถ้าเป็นไฟล์ .zip ให้ทำการแตกไฟล์และจัดการชื่อไฟล์ ---
        if file_ext.lower() == ".zip":
            extract_folder = os.path.join(download_path, f"{idCode}_extracted")
            os.makedirs(extract_folder, exist_ok=True)

            with zipfile.ZipFile(download_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
                print(f"📂 แตกไฟล์ ZIP แล้วที่: {extract_folder}")

            # --- เปลี่ยนชื่อและย้ายไฟล์ออกมาชั้นนอก ---
            for idx, filename in enumerate(sorted(os.listdir(extract_folder)), start=1):
                old_path = os.path.join(extract_folder, filename)

                # ข้ามโฟลเดอร์ย่อย (ถ้ามี)
                if os.path.isdir(old_path):
                    continue

                ext = os.path.splitext(filename)[1]
                # เพิ่มเลขลำดับเพื่อไม่ให้ชื่อไฟล์ซ้ำกัน
                new_name = f"{idCode}_{idx:02d}{ext}"  # เช่น 2716007306_01.csv
                new_path = os.path.join(download_path, new_name)  # ชั้นนอก

                os.rename(old_path, new_path)
                print(f"📤 ย้ายและเปลี่ยนชื่อ {filename} → {new_name}")

            # --- ลบโฟลเดอร์ที่แตกไฟล์ (ถ้าไม่ต้องการเก็บไว้) ---
            os.rmdir(extract_folder)

        print("✅ ดาวน์โหลดและประมวลผลไฟล์เสร็จสิ้น")

    except Exception as e:
        print(f"❌ ไม่พบปุ่ม Download หรือเกิดข้อผิดพลาด: {e}")
        print("🔄 ทำการ logout ทันที...")
        try:
            page.get_by_role("button", name="logout").click()
            print("✅ Logout สำเร็จ (จาก error handler)")
            logged_out = True
        except:
            print("ไม่สามารถ logout ได้")
            logged_out = False

    # ปิดหน้าต่างและ logout (เฉพาะเมื่อยังไม่ได้ logout)
    if not logged_out:
        try:
            page.get_by_role("img", name="close").click()
        except:
            print("ไม่พบปุ่ม close")

        try:
            page.get_by_role("button", name="logout").click()
            print("✅ Logout สำเร็จ")
        except:
            print("ไม่พบปุ่ม logout")

















    # page.pause() # รอให้หน้าโหลดเสร็จ //////////





    # ---------------------
    context.close()
    browser.close()






   


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright, "PMSMK02", "JANJAW555", "PKGC007837", "4126048820")


    
 

