from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from playwright.sync_api import Playwright, sync_playwright, expect
from pydantic import BaseModel, Field
import requests
import shutil
import os
import subprocess
import psutil
import platform
import socket
import chardet
import codecs
from datetime import datetime
import re

app = FastAPI(title="TTB Statement API", description="API สำหรับดาวน์โหลดใบแจ้งยอดบัญชีจาก TTB Business One")

# กำหนดโฟลเดอร์สำหรับดาวน์โหลดไฟล์
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

class UpdateRequest(BaseModel):
    folder_path: str = Field(..., example="/home/satement02/autoClick-Statement-SCB")
    repo_url: str = Field(..., example="git@github.com:AGScorp/autoClick-Statement-SCB.git")
# Your existing functions...








# Helper functions
def post_data_to_google_script(url, data):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        # print("Sending data to Google Script...")
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Error sending data to Google Script: {err}")

def format_number(number):
    str_number = str(number)

    if len(str_number) < 4:
        return str_number
    else:
        # นำตัวเลขที่อยู่ในตำแหน่งแรกมาต่อหลัง
        formatted_number = str_number[:-3] + '-' + str_number[-3:]
        return formatted_number[-5:]







@app.post("/run")

def run_playwright(username: str, password: str, client_code: str, account_no: str):
    with sync_playwright() as playwright:
        run(playwright, username, password, client_code, account_no)
    return {"status": "success"}



def get_full_xpath(element):
    components = []
    while element:
        tag_name = element.evaluate("e => e.tagName.toLowerCase()")
        if tag_name == "html":
            components.append(tag_name)
            break
        parent = element.evaluate_handle("e => e.parentElement")
        children = element.evaluate_handle("e => Array.from(e.parentElement.children).filter(c => c.tagName.toLowerCase() === e.tagName.toLowerCase())")
        element_index = element.evaluate("(e, children) => children.indexOf(e)", children)
        components.append(f"{tag_name}[{element_index + 1}]")
        element = parent
    components.reverse()
    return "/" + "/".join(components)

def convert_csv_to_utf8(file_path):
    """
    แปลงไฟล์ CSV เป็น UTF-8 encoding

    Args:
        file_path (str): พาธของไฟล์ที่ต้องการแปลง

    Returns:
        str: พาธของไฟล์ที่แปลงแล้ว (เหมือนกับไฟล์ต้นฉบับ)
    """
    try:
        # ตรวจสอบ encoding ของไฟล์
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            source_encoding = result['encoding']
            confidence = result['confidence']

        print(f"Detected encoding: {source_encoding} with confidence: {confidence}")

        # ถ้าไม่ใช่ UTF-8 ให้แปลงเป็น UTF-8
        if source_encoding and source_encoding.lower() != 'utf-8':
            # อ่านไฟล์ด้วย encoding ที่ตรวจพบ
            with codecs.open(file_path, 'r', encoding=source_encoding, errors='replace') as f_input:
                content = f_input.read()

            # เขียนไฟล์ใหม่ด้วย UTF-8
            with codecs.open(file_path, 'w', encoding='utf-8') as f_output:
                f_output.write(content)

            print(f"Converted file from {source_encoding} to UTF-8: {file_path}")
        else:
            print(f"File is already in UTF-8 format or encoding could not be detected: {file_path}")

        return file_path
    except Exception as e:
        print(f"Error converting file to UTF-8: {e}")
        return file_path  # คืนค่าพาธเดิมในกรณีที่มีข้อผิดพลาด

def extract_number(xpath_string):
    # Regex pattern เพื่อจับเลขที่ต้องการ
    pattern = r'/html/body/div\[1\]/div/div\[2\]/div\[2\]/table/tbody/tr\[7\]/td\[2\]/table/tbody/tr\[(\d+)\]/td\[4\]/a'
    match = re.search(pattern, xpath_string)

    if match:
        return int(match.group(1))
    return None

def extract_number_from_xpath(xpath_string):
    # เจาะจง regex เพื่อดึงตัวเลขจาก XPath ที่ต้องการ
    pattern = r'/html/body\[\d+\]/div\[\d+\]/div\[\d+\]/div\[\d+\]/div\[\d+\]/table\[\d+\]/tbody\[\d+\]/tr\[(\d+)\]/td\[\d+\]/table\[\d+\]/tbody\[\d+\]/tr\[(\d+)\]/td\[\d+\]'
    match = re.search(pattern, xpath_string)

    if match:
        # ต้องการตัวเลขจาก tr ล่าสุด
        return int(match.group(2))
    return None












def run(playwright: Playwright, username: str, password: str, client_code: str, account_no: str) -> None:
    """
    ฟังก์ชันหลักสำหรับการทำงานกับ Playwright เพื่อดาวน์โหลดใบแจ้งยอดบัญชี

    Args:
        playwright: Playwright instance
        username: ชื่อผู้ใช้สำหรับเข้าสู่ระบบ
        password: รหัสผ่านสำหรับเข้าสู่ระบบ
        client_code: รหัสลูกค้า
        account_no: เลขที่บัญชี
    """
    # แปลงเลขบัญชีให้อยู่ในรูปแบบที่ต้องการ
    idCode = account_no

    # เปิด browser
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

   

    page.get_by_role("cell", name="Krungthai Corporate Online :").get_by_role("list").click()
    page.locator("#select2-drop").get_by_text("6946").click()

    page.get_by_role("cell", name="Krungthai Corporate Online :").locator("img").nth(2).click()
    page.get_by_role("link", name="16").click()

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
            new_name = f"{idCode}{ext}"  # name01.xlsx
            new_path = os.path.join(download_path, new_name)  # ชั้นนอก

            os.rename(old_path, new_path)
            print(f"📤 ย้ายและเปลี่ยนชื่อ {filename} → {new_name}")

        # --- ลบโฟลเดอร์ที่แตกไฟล์ (ถ้าไม่ต้องการเก็บไว้) ---
        os.rmdir(extract_folder)




    # ปิดหน้าต่างและ logout
    page.get_by_role("img", name="close").click()
    page.get_by_role("button", name="logout").click()














    # ---------------------
    context.close()
    browser.close()




@app.get("/get-file/", summary="ดาวน์โหลดใบแจ้งยอดบัญชี", description="บริการนี้ใช้เพื่อดึงไฟล์ใบแจ้งยอดบัญชีที่เจาะจงตามชื่อไฟล์จากเซิร์ฟเวอร์.")
def get_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/vnd.ms-excel', filename=filename)
    else:
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ที่ระบุ")

@app.get("/status", summary="ตรวจสอบสถานะเซิร์ฟเวอร์", description="แสดงข้อมูลสถานะการทำงานของเซิร์ฟเวอร์ เช่น CPU, RAM, และข้อมูลระบบอื่นๆ")
def get_server_status():
    try:
        # ข้อมูลระบบ
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(socket.gethostname())
        os_info = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()

        # ข้อมูลทรัพยากร
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = f"{memory.used / (1024 * 1024 * 1024):.2f} GB"
        memory_total = f"{memory.total / (1024 * 1024 * 1024):.2f} GB"

        # ข้อมูลดิสก์
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = f"{disk.used / (1024 * 1024 * 1024):.2f} GB"
        disk_total = f"{disk.total / (1024 * 1024 * 1024):.2f} GB"

        # ข้อมูลเวลาทำงาน
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_days = uptime.days
        uptime_hours, remainder = divmod(uptime.seconds, 3600)
        uptime_minutes, uptime_seconds = divmod(remainder, 60)
        uptime_str = f"{uptime_days} วัน {uptime_hours} ชั่วโมง {uptime_minutes} นาที {uptime_seconds} วินาที"

        # ข้อมูลไฟล์ที่ดาวน์โหลด
        downloaded_files = []
        if os.path.exists(DOWNLOAD_DIR):
            downloaded_files = os.listdir(DOWNLOAD_DIR)

        # สร้าง response
        return {
            "status": "online",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "hostname": hostname,
                "ip_address": ip_address,
                "os": os_info,
                "python_version": python_version
            },
            "resources": {
                "cpu": {
                    "usage_percent": cpu_percent
                },
                "memory": {
                    "usage_percent": memory_percent,
                    "used": memory_used,
                    "total": memory_total
                },
                "disk": {
                    "usage_percent": disk_percent,
                    "used": disk_used,
                    "total": disk_total
                }
            },
            "uptime": uptime_str,
            "downloads": {
                "total_files": len(downloaded_files),
                "files": downloaded_files[:10],  # แสดงเฉพาะ 10 ไฟล์แรก
                "download_dir": DOWNLOAD_DIR
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลสถานะ: {str(e)}")

@app.post('/update-code', summary="อัพเดทโค้ด API จาก git repository", description="ทำการ git pull โดยใช้ URL ที่ระบุเพื่ออัพเดทโค้ดลงใน folder ที่กำหนด")
async def update_code(request: UpdateRequest):
    try:
        # Extract folder path and repo URL from the request
        path_to_repo = request.folder_path
        repo_url = request.repo_url

        # Perform `git pull` using the provided SSH URL directly
        result_pull = subprocess.run(
            ["git", "pull", repo_url],
            cwd=path_to_repo,
            text=True,
            capture_output=True
        )

        if result_pull.returncode != 0:
            raise Exception(result_pull.stderr)

        return {"status": "success", "message": result_pull.stdout}

    except Exception as e:
        # logging.error(f"Error during git pull: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during git pull: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("TTB_STM_01:app", host="0.0.0.0", port=8002, reload=True)
