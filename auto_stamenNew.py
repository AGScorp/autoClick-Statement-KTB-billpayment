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

     
    browser = playwright.chromium.launch(headless=False)
    # executable_path = "/usr/bin/google-chrome"
    # downloads_path = "/home/ags-test-bot/AutoClick/autoClickAccountStatement"
    # browser = playwright.chromium.launch(headless=False,executable_path=executable_path,args=["--no-sandbox","--disable-setuid-sandbox"],downloads_path=downloads_path,channel="stable",chromium_sandbox=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.bizgrowing.krungthai.com/corporate/Login.do?cmd=init")



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

    

#เลือกวันที่
    page.get_by_role("cell", name="Krungthai Corporate Online :").locator("img").nth(2).click()
    page.get_by_role("link", name="1", exact=True).click()





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

 

    # --- คลิกปุ่มดาวน์โหลด ---
    page.get_by_role("button", name="Download").click()


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
            new_name = f"{idCode}{ext}"  # เช่น 2716007306_01.csv
            new_path = os.path.join(download_path, new_name)  # ชั้นนอก

            os.rename(old_path, new_path)
            print(f"📤 ย้ายและเปลี่ยนชื่อ {filename} → {new_name}")

        # --- ลบโฟลเดอร์ที่แตกไฟล์ (ถ้าไม่ต้องการเก็บไว้) ---
        os.rmdir(extract_folder)

 # --- อ่านและแปลง encoding จาก CSV ที่โหลด ---
        data = []
        csv_path = os.path.join(download_path, new_name)

        # ลองอ่านด้วย encoding ต่าง ๆ
        encodings_to_try = ['utf-8', 'utf-8-sig', 'cp874', 'tis-620', 'ISO-8859-11']
        for enc in encodings_to_try:
            try:
                with open(csv_path, 'r', encoding=enc) as src_file:
                    lines = src_file.readlines()
                    print(f"✅ อ่านไฟล์สำเร็จด้วย encoding: {enc}")
                    break
            except UnicodeDecodeError as e:
                print(f"❌ อ่านไม่ได้ด้วย encoding: {enc} → {e}")
                lines = None

       # ถ้าอ่านได้ → เขียนทับใหม่แบบตัด 2 แถวแรก
        if lines:
            lines = lines[2:]  # 🔥 ลบ 2 แถวแรก

            with open(csv_path, 'w', encoding='utf-8', newline='') as dst_file:
                dst_file.writelines(lines)
            print(f"📄 เขียนทับไฟล์ด้วย UTF-8 แล้ว และลบ 2 แถวแรก → {csv_path}")

            # อ่านข้อมูลเข้า data
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    data.append(row)
        else:
            print("⚠️ ไม่สามารถอ่านไฟล์ CSV ได้เลยสัก encoding")




    
                    





















    # page.pause() # รอให้หน้าโหลดเสร็จ //////////
    # ปิดหน้าต่างและ logout
    page.get_by_role("button", name="logout").click()
    # page.get_by_role("img", name="close").click()
    # page.get_by_role("button", name="logout").click()





    # ---------------------
    context.close()
    browser.close()






   


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright, "PMSMK02", "JANJAW555", "PKGC007837", "4126048820")


    
 

