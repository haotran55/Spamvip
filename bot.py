import telebot
import subprocess
import sys
from requests import post, Session
import time
import datetime
import threading
from urllib.parse import urlparse
import psutil
import tempfile
import random
from gtts import gTTS
import re
import string
import os
from threading import Lock
import requests
import sqlite3
from telebot import types
from time import strftime
import queue
import pytz
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.types import Message 
from aiogram.filters import Command
from flask import Flask
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # ✅ Đúng
from telegram.ext import Application
admin_diggory = "ad_an_danhso5" 
name_bot = "HaoEsports"
zalo = "0585019743"
web = "https://dichvukey.site/"
facebook = "no"
bot=telebot.TeleBot("7920158658:AAGyY9jA2B5Z3_n3vZzzQBDYaJoAddPqZ7s")
#phu 8127007530:AAG1b4w__xXvIrAr7woZjN8BrC_l3g1hBwI
print("Bot đã được khởi động thành công")
dp = Dispatcher()
scheduler = AsyncIOScheduler()
users_keys = {}
key = ""
user_cooldown = {}
share_log = []
auto_spam_active = False
last_sms_time = {}
global_lock = Lock()
allowed_users = []
processes = []
ADMIN_ID =  7713922358 #nhớ thay id nhé nếu k thay k duyệt dc vip đâu v.L..ong.a
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
last_command_time = {}

last_command_timegg = 0

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot Telegram đang chạy!"
    
def check_command_cooldown(user_id, command, cooldown):
    current_time = time.time()
    
    if user_id in last_command_time and current_time - last_command_time[user_id].get(command, 0) < cooldown:
        remaining_time = int(cooldown - (current_time - last_command_time[user_id].get(command, 0)))
        return remaining_time
    else:
        last_command_time.setdefault(user_id, {})[command] = current_time
        return None

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()

def TimeStamp():
  now = str(datetime.date.today())
  return now

#vLong zz#v
def load_users_from_database():
  cursor.execute('SELECT user_id, expiration_time FROM users')
  rows = cursor.fetchall()
  for row in rows:
    user_id = row[0]
    expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
    if expiration_time > datetime.datetime.now():
      allowed_users.append(user_id)


def save_user_to_database(connection, user_id, expiration_time):
  cursor = connection.cursor()
  cursor.execute(
    '''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
  connection.commit()
###

vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')


###
#zalo ...07890416.31

####
start_time = time.time()



def fetch_data(user_id):
    try:
        url = f'https://api.ffcommunity.site/info.php?uid={user_id}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

@bot.message_handler(commands=['ff'])
def handle_command(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "<blockquote>Sử dụng: /ff ID\nVí dụ: /ff 1733997441</blockquote>", parse_mode="HTML")
        return
    
    command, user_id = parts
    if not user_id.isdigit():
        bot.reply_to(message, "<blockquote>ID không hợp lệ. Vui lòng nhập ID số.</blockquote>", parse_mode="HTML")
        return

    try:
        data = fetch_data(user_id)
        basic_info = data
        clan_info = data.get('Guild Information', {})
        leader_info = data.get('Guild Leader', {})
        avatar_url = basic_info.get('AccountAvatarId', 'Hiện tại đang bảo chì')

        def get_value(key, data_dict):
            return data_dict.get(key, "Hiện tại server đang quá tải, vui lòng chờ")

        info_text = f"""
<blockquote>
<b>Thông tin cơ bản:</b>
Avatar: <a href="{avatar_url}">Nhấn để xem</a>
Nickname: {get_value('AccountName', basic_info)}
Cấp độ: {get_value('AccountLevel', basic_info)}
Khu vực: {get_value('AccountRegion', basic_info)}
Xếp hạng Sinh Tồn: {get_value('BrRank', basic_info)}
Tổng Sao Tử Chiến: {get_value('CsRank', basic_info)}
Số lượt thích: {get_value('AccountLikes', basic_info)}
Lần đăng nhập gần nhất: {get_value('AccountLastLogin', basic_info)}
Ngôn ngữ: {get_value('AccountLanguage', basic_info)}
Tiểu sử game: {get_value('AccountSignature', basic_info)}

<b>Thông tin quân đoàn:</b>
Tên quân đoàn: {get_value('GuildName', clan_info)}
Cấp độ quân đoàn: {get_value('GuildLevel', clan_info)}
Sức chứa: {get_value('GuildCapacity', clan_info)}
Số thành viên hiện tại: {get_value('GuildMember', clan_info)}
Chủ quân đoàn: {get_value('LeaderName', leader_info)}
Cấp độ chủ quân đoàn: {get_value('LeaderLevel', leader_info)}
</blockquote>
"""

        bot.reply_to(message, info_text, parse_mode='HTML')

    except Exception as e:
        bot.reply_to(message, "<blockquote>Đã xảy ra lỗi</blockquote>", parse_mode="HTML")


# Đường dẫn file lưu ID người dùng
ID_FILE = "id.json"

# Hàm gửi tin nhắn đến tất cả user đã lưu
async def send_message_to_all(text):
    try:
        with open(ID_FILE, "r", encoding="utf-8") as file:
            chat_ids = json.load(file)
    except FileNotFoundError:
        chat_ids = []
    except json.JSONDecodeError:
        chat_ids = []

    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id, text)
            logging.info(f"📤 Đã gửi tin nhắn đến chat {chat_id}")
        except Exception as e:
            logging.error(f"❌ Lỗi gửi tin nhắn đến {chat_id}: {e}")

# Hàm kiểm tra giờ và gửi thông báo
async def check_time_and_send_message():
    from datetime import datetime
    now = datetime.now()
    hour = now.hour

    if hour == 7:
        message = "🌞 Chào buổi sáng! Hãy bắt đầu ngày mới với năng lượng tích cực!"
    elif hour == 12:
        message = "💤 Đã 12 giờ trưa, nghỉ ngơi một chút để tái tạo năng lượng!"
    elif hour == 18:
        message = "🌇 Chào buổi chiều! Hy vọng buổi tối của bạn sẽ thật thư giãn!"
    elif hour == 0:
        message = "🌙 Đã 12 giờ đêm, hãy đi ngủ sớm để có một ngày mới tràn đầy sức sống!"
    else:
        message = f"🕰️ Hiện tại là {hour} giờ. Hãy tận dụng thời gian một cách hiệu quả!"

    await send_message_to_all(message)

# Lưu chat ID vào danh sách khi có người nhắn tin bot
@dp.message()
async def save_chat_id(message: Message):
    try:
        with open(ID_FILE, "r", encoding="utf-8") as file:
            chat_ids = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        chat_ids = []

    if message.chat.id not in chat_ids:
        chat_ids.append(message.chat.id)
        with open(ID_FILE, "w", encoding="utf-8") as file:
            json.dump(chat_ids, file, indent=4)
        await message.answer("✅ Bạn đã đăng ký nhận thông báo tự động!")

# Lệnh `/broadcast` để gửi thông báo thủ công
@dp.message(Command("broadcast"))
async def manual_broadcast(message: Message):
    if message.from_user.id == 123456789:  # Thay bằng ID admin của bạn
        text = message.text.replace("/broadcast ", "")
        await send_message_to_all(text)
        await message.answer("📢 Đã gửi thông báo đến tất cả người dùng!")
    else:
        await message.answer("⛔ Bạn không có quyền sử dụng lệnh này.")

# Cấu hình lịch chạy tự động
scheduler = AsyncIOScheduler()
scheduler.add_job(check_time_and_send_message, "interval", hours=1)  # Chạy mỗi 1 giờ


@bot.message_handler(commands=['start'])
def send_help(message):
    bot.reply_to(message, """<blockquote>
╔══════════════════╗  
     📌         *DANH SÁCH LỆNH*  
╚══════════════════╝  
 _____________________________________
| /ff : check acc xem thông tin 
| /gg : tìm ảnh 
| /spam : spam smm
| /randomvideo : video gái xinh
| /tv : chuyển đổi ngôn ngữ 
| /spamvip : spam vip
| /like : buff like
| /getkey : lấy key 
| /key : nhập key
|—————————————————
                     Lệnh Admin
|____________________________
| /off : tắt bot
| /on : bật bot
| /broadcast
| /rs : khởi động lại bot
|____________________________
</blockquote>""", parse_mode="HTML")

API_BASE_URL = "https://freefire-virusteam.vercel.app"

def get_vip_key():
    try:
        response = requests.get("https://dichvukey.site/keyvip.txt", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException:
        return "default-key"  

VIP_KEY = get_vip_key()

region_translation = {
    "VN": "Việt Nam", "ID": "Indonesia", "TH": "Thái Lan",
    "SG": "Singapore", "TW": "Đài Loan", "EU": "Châu Âu",
    "US": "Hoa Kỳ", "BR": "Brazil", "MX": "Mexico",
    "IN": "Ấn Độ", "KR": "Hàn Quốc", "PK": "Pakistan",
    "BD": "Bangladesh", "RU": "Nga", "MENA": "Trung Đông & Bắc Phi",
    "LA": "Châu Mỹ Latinh"
}

def call_api(endpoint, params=None):
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"status": "error", "message": "Sever quá tải hoặc lỗi kết nối"}

def check_user_permission(message):
    user_id = message.from_user.id
    today_day = datetime.date.today().day
    key_path = f"./user/{today_day}/{user_id}.txt"

    return user_id in allowed_users or os.path.exists(key_path)

def handle_api_error(message, error_message):
    bot.reply_to(message, f"<blockquote>❌ {error_message}</blockquote>", parse_mode="HTML")
####zalo 0789041631
### /like
@bot.message_handler(commands=['like'])
def like_handler(message):
    try:
        if not check_user_permission(message):
            bot.reply_to(message, "<blockquote>Bạn chưa nhập key! hãy /getkey hoặc /muavip ngay</blockquote>", parse_mode="HTML")
            return

        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "<blockquote>Sử dụng: /like ID\nVí dụ: /like 1733997441</blockquote>", parse_mode="HTML")
            return

        uid = args[1]
        if not uid.isdigit():
            bot.reply_to(message, "<blockquote>ID không hợp lệ. Vui lòng nhập ID số.</blockquote>", parse_mode="HTML")
            return

        url = f"{API_BASE_URL}/likes1"
        response = requests.get(url, params={"key": VIP_KEY, "uid": uid}, timeout=10)
        data = response.json()

        if "message" in data:
            msg_content = data["message"]
            if isinstance(msg_content, str):
                reply_text = f"<blockquote>⚠️ {msg_content}</blockquote>"
            elif isinstance(msg_content, dict):
                reply_text = (
                    f"<blockquote>\n"
                    f"🎯 <b>Kết quả buff like:</b>\n"
                    f"👤 <b>Tên:</b> {msg_content.get('Name', 'Không xác định')}\n"
                    f"🆔 <b>UID:</b> {msg_content.get('UID', 'Không xác định')}\n"
                    f"🌎 <b>Khu vực:</b> {msg_content.get('Region', 'Không xác định')}\n"
                    f"📊 <b>Level:</b> {msg_content.get('Level', 'Không xác định')}\n"
                    f"👍 <b>Like trước:</b> {msg_content.get('Likes Before', 'Không xác định')}\n"
                    f"✅ <b>Like sau:</b> {msg_content.get('Likes After', 'Không xác định')}\n"
                    f"➕ <b>Tổng cộng:</b> {msg_content.get('Likes Added', 'Không xác định')} like\n"
                    f"</blockquote>"
                )
            else:
                reply_text = "<blockquote>Không đúng định dạng phản hồi</blockquote>"

            bot.reply_to(message, reply_text, parse_mode="HTML")
        else:
            bot.reply_to(message, "<blockquote>❌ Không nhận được phản hồi hợp lệ từ server</blockquote>", parse_mode="HTML")
            
    except requests.RequestException as e:
        bot.reply_to(message, "<blockquote>❌ Lỗi kết nối đến server. Vui lòng thử lại sau.</blockquote>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, "<blockquote>❌ Đã xảy ra lỗi. Vui lòng thử lại sau.</blockquote>", parse_mode="HTML")

#gg
API_URL = "https://dichvukey.site/apivl/gg.php?gg="
@bot.message_handler(commands=['gg'])
def search_google_image(message):
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) == 2:
        query = command_parts[1].strip()
        api_request_url = API_URL + requests.utils.quote(query)
        
        try:
            response = requests.get(api_request_url)
            response_data = response.json()
            
            if "image_url" in response_data and "caption" in response_data:
                image_url = response_data["image_url"]
                caption = response_data["caption"]
                
                bot.send_photo(message.chat.id, photo=image_url, caption=caption, parse_mode="Markdown")
            else:
                bot.reply_to(message, "không tìm thấy hình ảnh nào.")
        except Exception as e:
            bot.reply_to(message, "Lỗi khi tìm kiếm hình ảnh.")
            print(f"Lỗi")
    else:
        bot.reply_to(message, "/gg gái xinh")
### tiep theo codeby HàoEsports


def TimeStamp():
    return datetime.datetime.now().strftime("%Y-%m-%d")
    
@bot.message_handler(commands=['getkey'])
def startkey(message):
    user_id = message.from_user.id
    today_day = datetime.date.today().day
    key = "HaoEsport" + str(user_id * today_day - 2007)

    api_token = '64f857ff1b02a144e1073c7e'
    key_url = f"https://dichvukey.site/key.html?key={key}"

    try:
        response = requests.get(f'https://link4m.co/api-shorten/v2?api={api_token}&url={key_url}')
        response.raise_for_status()
        url_data = response.json()
        print(key)

        if 'shortenedUrl' in url_data:
            url_key = url_data['shortenedUrl']
            text = (f'Link Lấy Key Ngày {TimeStamp()} LÀ: {url_key}\n'
                    'KHI LẤY KEY XONG, DÙNG LỆNH /key HaoEsport ĐỂ TIẾP TỤC Hoặc /muavip đỡ vượt tốn thời gian nhé')
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, 'Lỗi.')
    except requests.RequestException:
        bot.reply_to(message, 'Lỗi.')

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Key Đã Vượt Là? đã vượt thì nhập /key chưa vượt thì /muavip nhé')
        return

    user_id = message.from_user.id
    key = message.text.split()[1]
    today_day = datetime.date.today().day
    expected_key = "HaoEsport" + str(user_id * today_day - 2007)  # Đảm bảo công thức khớp với công thức tạo key

    if key == expected_key:
        text_message = f'<blockquote>[ KEY HỢP LỆ ] NGƯỜI DÙNG CÓ ID: [ {user_id} ] ĐƯỢC PHÉP ĐƯỢC SỬ DỤNG CÁC LỆNH TRONG [/start]</blockquote>'
        video_url = 'https://v16m-default.akamaized.net/4e91716006f611b4064fb417539f7a57/66a9164c/video/tos/alisg/tos-alisg-pve-0037c001/o4VRzDLftQGT9YgAc2pAefIqZeIoGLgGAFIWtF/?a=0&bti=OTg7QGo5QHM6OjZALTAzYCMvcCMxNDNg&ch=0&cr=0&dr=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=2138&bt=1069&cs=0&ds=6&ft=XE5bCqT0majPD12fFa-73wUOx5EcMeF~O5&mime_type=video_mp4&qs=0&rc=PGloZWg2aTVoOGc7OzllZkBpanA0ZXA5cjplczMzODczNEAtXmAwMWEyXjUxNWFgLjYuYSNxZ3IyMmRrNHNgLS1kMS1zcw%3D%3D&vvpl=1&l=20240730103502EC9CCAF9227AE804B708&btag=e00088000'  # Đổi URL đến video của bạn
        bot.send_video(message.chat.id, video_url, caption=text_message, parse_mode='HTML')
        
        user_path = f'./user/{today_day}'
        os.makedirs(user_path, exist_ok=True)
        with open(f'{user_path}/{user_id}.txt', "w") as fi:
            fi.write("")
    else:
        bot.reply_to(message, 'KEY KHÔNG HỢP')
     
        if bot_active:
          pass  # ✅ Tránh lỗi IndentationError

        bot.infinity_polling()  # ✅ Được đặt bên ngoài `if`


