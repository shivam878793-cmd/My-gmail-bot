import telebot
import sqlite3
import time
import random
import string
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '7990556564:AAFYUQrYcQ7UmwbmFdjPShBFk_kLVYepRpA'
ADMIN_ID = 8031127296

bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect('gmail_bot.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            referred_by INTEGER,
            completed_single_tasks INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail TEXT,
            password TEXT,
            assigned_to INTEGER DEFAULT NULL,
            assigned_at INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'AVAILABLE'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            user_id INTEGER PRIMARY KEY,
            task_type TEXT,
            task_id_list TEXT,
            started_at INTEGER,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) as count FROM task_pool")
    if cursor.fetchone()['count'] == 0:
        for i in range(1, 30):
            cursor.execute(
                "INSERT INTO task_pool (gmail, password) VALUES (?, ?)", 
                (f"testuser{i}@gmail.com", f"Pass{random.randint(1000,9999)}")
            )
    
    conn.commit()
    conn.close()

init_db()

# --- HELPER FUNCTIONS ---
def register_user(user_id, referrer_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referrer_id))
        if referrer_id:
            cursor.execute("UPDATE users SET balance = balance + 1.0 WHERE user_id = ?", (referrer_id,))
            try:
                bot.send_message(referrer_id, "🎉 Alert! Aapke link se koi join hua hai. You got ₹1!")
            except:
                pass
        conn.commit()
    conn.close()

def check_and_release_expired_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    current_time = int(time.time())
    expiry_limit = current_time - 600
    
    cursor.execute("SELECT user_id FROM sessions WHERE started_at < ? AND status = 'PENDING'", (expiry_limit,))
    expired_sessions = cursor.fetchall()
    
    for session in expired_sessions:
        uid = session['user_id']
        cursor.execute("SELECT task_id_list FROM sessions WHERE user_id = ?", (uid,))
        res = cursor.fetchone()
        if res and res['task_id_list']:
            ids = res['task_id_list'].split(',')
            for t_id in ids:
                cursor.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(t_id),))
        
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (uid,))
        try:
            bot.send_message(uid, "⏰ Time Out! Aapne 10 minute me task submit nahi kiya, isliye task cancel ho gaya.")
        except:
            pass
            
    conn.commit()
    conn.close()

# --- KEYBOARDS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📨 Get Gmail Task")
    btn2 = types.KeyboardButton("💰 Wallet")
    btn3 = types.KeyboardButton("👥 Invite & Earn")
    btn4 = types.KeyboardButton("💸 Withdraw")
    btn5 = types.KeyboardButton("📚 Help & Tutorial")
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    return markup

def task_options_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("1 Gmail Task", callback_data="task_single"),
        types.InlineKeyboardButton("0/10 Gmail Task", callback_data="task_batch")
    )
    return markup

def task_action_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Done", callback_data="task_done"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="task_cancel")
    )
    return markup

# --- COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    text = message.text.split()
    referrer_id = None
    if len(text) > 1 and text[1].isdigit():
        referrer_id = int(text[1])
        if referrer_id == user_id:
            referrer_id = None
            
    register_user(user_id, referrer_id)
    bot.send_message(
        message.chat.id, 
        "👋 Welcome! Gmail Task Bot me aapka swagat hai.\nNiche diye gaye buttons se kaam shuru karein.", 
        reply_markup=main_menu()
    )

# --- REPLY KEYBOARD LOGIC ---
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    check_and_release_expired_tasks()
    user_id = message.from_user.id
    register_user(user_id)
    
    if message.text == "📨 Get Gmail Task":
        bot.send_message(message.chat.id, "Select your task option:", reply_markup=task_options_menu())
        
    elif message.text == "💰 Wallet":
        conn = get_db_connection()
        user = conn.execute("SELECT balance, completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        bot.send_message(message.chat.id, f"💳 **Aapka Wallet Details:**\n\n💰 Total Balance: ₹{user['balance']}\n✅ Completed Single Tasks: {user['completed_single_tasks']}")
        
    elif message.text == "👥 Invite & Earn":
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={user_id}"
        bot.send_message(message.chat.id, f"👥 **Invite & Earn Program:**\n\nPer Invite aapko **₹1** milega.\nAapka unique referral link ye raha:\n\n`{invite_link}`", parse_mode="Markdown")
        
    elif message.text == "💸 Withdraw":
        conn = get_db_connection()
        user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        
        if user['balance'] >= 15.0:
            msg = bot.send_message(message.chat.id, "💰 Please send your **UPI ID** for withdrawal:")
            bot.register_next_step_handler(msg, process_withdrawal)
        else:
            bot.send_message(message.chat.id, "❌ Minimum withdrawal amount **₹15** hai. Aapka balance kam hai.")
            
    elif message.text == "📚 Help & Tutorial":
        bot.send_message(message.chat.id, "📹 **Help & Tutorial Video:**\n\n[Yahan Admin Task Kaise Karna Hai Uska Video Add Kar Sakta Hai]")

# --- WITHDRAWAL WORKFLOW ---
def process_withdrawal(message):
    user_id = message.from_user.id
    upi_id = message.text
    
    conn = get_db_connection()
    user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    
    if user['balance'] < 15.0:
        bot.send_message(message.chat.id, "❌ Verification Failed: Balance insufficient.")
        conn.close()
        return
        
    balance_to_withdraw = user['balance']
    conn.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    bot.send_message(message.chat.id, f"✅ Request Submitted! ₹{balance_to_withdraw} ka withdrawal process ho raha hai admin panel par.")
    
    bot.send_message(
        ADMIN_ID, 
        f"🚨 **NEW WITHDRAWAL REQUEST** 🚨\n\n👤 User ID: `{user_id}`\n💰 Amount: ₹{balance_to_withdraw}\n📱 UPI ID: `{upi_id}`", 
        parse_mode="Markdown"
    )

# --- CALLBACK QUERY HANDLERS (Inline Buttons) ---
@bot.callback_query_handler(func=lambda call: True and not call.data.startswith('adm_'))
def handle_callbacks(call):
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    conn = get_db_connection()
    active_session = conn.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,)).fetchone()

    if call.data == "task_single":
        if active_session:
            bot.answer_callback_query(call.id, "❌ Aapka ek task already chal raha hai!")
            bot.send_message(chat_id, "Pehle chal rahe task ko Done ya Cancel karein.")
            conn.close()
            return
            
        task = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 1").fetchone()
        if not task:
            bot.answer_callback_query(call.id, "😢 No Tasks Available right now!")
            conn.close()
            return
            
        current_time = int(time.time())
        conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, task['id']))
        conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'SINGLE', ?, ?)", (user_id, str(task['id']), current_time))
        conn.commit()
        
        task_msg = f"📨 **Your Single Gmail Task:**\n\n📧 **Gmail:** `{task['gmail']}`\n🔑 **Password:** `{task['password']}`\n\n⚠️ **Note:** Create Gmail And Submit Under 10M. Varna 10 minute me automatic cancel ho jayega."
        bot.edit_message_text(task_msg, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=task_action_buttons())

    elif call.data == "task_batch":
        if active_session:
            bot.answer_callback_query(call.id, "❌ Aapka ek task already chal raha hai!")
            conn.close()
            return
            
        user_data = conn.execute("SELECT completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if user_data['completed_single_tasks'] < 10:
            bot.answer_callback_query(call.id, "❌ Access Denied!", show_alert=True)
            bot.send_message(chat_id, f"🔒 **complete first 10 gmail** single task mode se! (Aapka current score: {user_data['completed_single_tasks']}/10)")
            conn.close()
            return
            
        tasks = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 10").fetchall()
        if len(tasks) < 10:
            bot.answer_callback_query(call.id, "😢 10 Gmails bulk pool me ready nahi hain!", show_alert=True)
            conn.close()
            return
            
        current_time = int(time.time())
        task_ids = [str(t['id']) for t in tasks]
        comma_separated_ids = ",".join(task_ids)
        
        for t in tasks:
            conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, t['id']))
            
        conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'BATCH_10', ?, ?)", (user_id, comma_separated_ids, current_time))
        conn.commit()
        
        batch_text = "📨 **Your 10x Batch Gmail Task:**\n\n"
        for idx, t in enumerate(tasks, 1):
            batch_text += f"{idx}. `{t['gmail']}` | `{t['password']}`\n"
        batch_text += "\n⚠️ Create Gmails And Submit Under 10M. Varna list automatic expiration trigger ho jayegi."
        
        bot.edit_message_text(batch_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=task_action_buttons())

    elif call.data == "task_cancel":
        if not active_session:
            bot.answer_callback_query(call.id, "Koi active task nahi mila.")
            conn.close()
            return
            
        ids = active_session['task_id_list'].split(',')
        for t_id in ids:
            conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(t_id),))
            
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        
        bot.edit_message_text("❌ Task Cancelled. Credentials wapas open market pool me bhej diye gaye hain.", chat_id, call.message.message_id)

    elif call.data == "task_done":
        if not active_session:
            bot.answer_callback_query(call.id, "Koi active task nahi mila.")
            conn.close()
            return
            
        conn.execute("UPDATE sessions SET status = 'DONE_SUBMITTED' WHERE user_id = ?", (user_id,))
        conn.commit()
        
        msg = bot.send_message(chat_id, "📸 Please **Submit Screenshot** proof validation ke liye:")
        bot.register_next_step_handler(msg, process_screenshot_proof, active_session['task_type'], active_session['task_id_list'])

    conn.close()

# --- SCREENSHOT PROOF VERIFICATION WORKFLOW ---
def process_screenshot_proof(message, task_type, task_id_list):
    user_id = message.from_user.id
    
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Proof rejected! Aapko screenshot hi bhejna hoga. Dobara task lijiye.")
        conn = get_db_connection()
        ids = task_id_list.split(',')
        for t_id in ids:
            conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(t_id),))
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return

    file_id = message.photo[-1].file_id
    
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 Approve", callback_data=f"adm_app_{user_id}_{task_type}_{task_id_list}"),
        types.InlineKeyboardButton("🔴 Reject", callback_data=f"adm_rej_{user_id}_{task_id_list}")
    )
    
    bot.send_photo(
        ADMIN_ID, 
        file_id, 
        caption=f"🛰️ **NEW TASK PROOF SUBMITTED**\n\n👤 User: `{user_id}`\n🗂️ Task Type: **{task_type}**\n📦 Task Database IDs: `{task_id_list}`",
        parse_mode="Markdown",
        reply_markup=admin_markup
    )
    
    bot.send_message(message.chat.id, "⏳ Aapka screenshot proof admin audit panel me chala gaya hai. Approval ka wait karein.")

# --- ADMIN PANEL PROOF AUDITING LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('adm_'))
def handle_admin_audit(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Not Authorized!")
        return
        
    data_parts = call.data.split('_')
    action = data_parts[1]
    target_user = int(data_parts[2])
    
    conn = get_db_connection()
    
    if action == "app":
        task_type = data_parts[3]
        task_id_list = data_parts[4]
        ids = task_id_list.split(',')
        
        for t_id in ids:
            conn.execute("UPDATE task_pool SET status = 'COMPLETED' WHERE id = ?", (int(t_id),))
            
        if task_type == "SINGLE":
            reward = 2.0
            conn.execute("UPDATE users SET balance = balance + ?, completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (reward, target_user))
        else:
            reward = 20.0
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, target_user))
            
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (target_user,))
        conn.commit()
        
        bot.edit_message_caption("🟢 Approved and Paid out successfully!", call.message.chat.id, call.message.message_id)
        try:
            bot.send_message(target_user, f"🎉 Congratulations! Admin ne aapka proof approve kar diya hai. Reward aapke wallet me add ho gaya hai.")
        except:
            pass
            
    elif action == "rej":
        task_id_list = data_parts[3]
        ids = task_id_list.split(',')
        
        for t_id in ids:
            conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(t_id),))
            
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (target_user,))
        conn.commit()
        
        bot.edit_message_caption("🔴 Rejected! Credentials recycled back into the market loop.", call.message.chat.id, call.message.message_id)
        try:
            bot.send_message(target_user, "❌ Aapka screenshot verification failed ho gaya. Admin ne task reject kiya hai. Kripya correct task dubara karein.")
        except:
            pass
            
    conn.close()

# --- BROADCAST COMMAND FOR ADMIN ---
@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        bot.send_message(ADMIN_ID, "Usage: `/broadcast Aapka message yahan`")
        return
        
    conn = get_db_connection()
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    
    count = 0
    for u in users:
        try:
            bot.send_message(u['user_id'], text_to_send)
            count += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(ADMIN_ID, f"📢 Broadcast successfully delivered to {count} users.")

# --- START BOT ---
print("🚀 Bot is live and running safely...")
bot.infinity_polling()
