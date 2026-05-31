import telebot
import sqlite3
import time
import random
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '7990556564:AAFYUQrYcQ7UmwbmFdjPShBFk_kLVYepRpA'
ADMIN_ID = 8031127296

bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect('gmail_bot.db', timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    
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
    
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Database Initialization Error: {e}")

# --- HELPER FUNCTIONS ---
def register_user(user_id, referrer_id=None):
    try:
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
    except Exception as e:
        print(f"Error in register_user: {e}")

def check_and_release_expired_tasks():
    try:
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
    except Exception as e:
        print(f"Error in expiry checker: {e}")

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

# --- ADMIN EXCLUSIVE COMMANDS ---

@bot.message_handler(commands=['addbalance'])
def admin_add_balance(message):
    """Admin isse kisi bhi user ke wallet me paise add kar sakta hai. Format: /addbalance USERID AMOUNT"""
    if message.from_user.id != ADMIN_ID:
        return
    try:
        raw_text = message.text.replace("/addbalance", "").strip()
        parts = raw_text.split()
        if len(parts) < 2:
            bot.send_message(ADMIN_ID, "❌ **Sahi Format Use Karein:**\n`/addbalance USER_ID AMOUNT`\n\nExample: `/addbalance 8031127296 50`", parse_mode="Markdown")
            return
            
        target_uid = int(parts[0])
        amount = float(parts[1])
        
        conn = get_db_connection()
        # Pehle check karo user registered hai ya nahi
        user_check = conn.execute("SELECT * FROM users WHERE user_id = ?", (target_uid,)).fetchone()
        if not user_check:
            # Agar user DB me nahi hai, toh use system me pehle register kar dete hain
            conn.execute("INSERT INTO users (user_id, balance) VALUES (?, 0.0)", (target_uid,))
            
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_uid))
        conn.commit()
        
        new_bal = conn.execute("SELECT balance FROM users WHERE user_id = ?", (target_uid,)).fetchone()['balance']
        conn.close()
        
        bot.send_message(ADMIN_ID, f"✅ **Success!**\n👤 User ID: `{target_uid}`\n➕ Added: ₹{amount}\n💰 New Balance: ₹{new_bal}", parse_mode="Markdown")
        
        try:
            bot.send_message(target_uid, f"🎁 **Wallet Update Alert!**\nAdmin ne aapke wallet me **₹{amount}** credit kiye hain.\n💰 Current Balance: ₹{new_bal}")
        except:
            pass
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Balance Add Error: {e}")

@bot.message_handler(commands=['checkuser'])
def admin_check_user(message):
    """Admin kisi bhi user ka wallet status dekh sakta hai. Format: /checkuser USERID"""
    if message.from_user.id != ADMIN_ID:
        return
    try:
        target_uid = message.text.replace("/checkuser", "").strip()
        if not target_uid or not target_uid.isdigit():
            bot.send_message(ADMIN_ID, "❌ Format: `/checkuser USER_ID`")
            return
            
        target_uid = int(target_uid)
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (target_uid,)).fetchone()
        conn.close()
        
        if user:
            bot.send_message(ADMIN_ID, f"🔍 **User Wallet Info:**\n👤 User ID: `{target_uid}`\n💰 Total Balance: ₹{user['balance']}\n✅ Completed Tasks: {user['completed_single_tasks']}", parse_mode="Markdown")
        else:
            bot.send_message(ADMIN_ID, "❌ Yeh User Bot ke database me nahi mila.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(commands=['addtask'])
def add_task_via_telegram(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        raw_text = message.text.replace("/addtask", "").strip()
        if not raw_text or ":" not in raw_text:
            bot.send_message(ADMIN_ID, "❌ Format:\n`/addtask username@gmail.com:password`", parse_mode="Markdown")
            return
        gmail, password = raw_text.split(":", 1)
        conn = get_db_connection()
        conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
        conn.commit()
        count = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        conn.close()
        bot.send_message(ADMIN_ID, f"✅ Added!\n📦 Stock: {count}", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(commands=['bulkadd'])
def bulk_add_tasks(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        raw_text = message.text.replace("/bulkadd", "").strip()
        if not raw_text:
            bot.send_message(ADMIN_ID, "❌ Format:\n\n`/bulkadd`\n`email1:pass1`\n`email2:pass2`", parse_mode="Markdown")
            return
        lines = raw_text.split("\n")
        success_count = 0
        error_count = 0
        conn = get_db_connection()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                try:
                    gmail, password = line.split(":", 1)
                    conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
                    success_count += 1
                except:
                    error_count += 1
            else:
                error_count += 1
        conn.commit()
        total_stock = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        conn.close()
        bot.send_message(ADMIN_ID, f"📦 **Bulk Import Status:**\n✅ Added: {success_count}\n❌ Failed: {error_count}\n🔥 Total Stock: {total_stock}", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Bulk Add Error: {e}")

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        return
    try:
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
        bot.send_message(ADMIN_ID, f"📢 Broadcast delivered to {count} users.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"Broadcast Error: {e}")

# --- REPLY KEYBOARD LOGIC ---
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    check_and_release_expired_tasks()
    user_id = message.from_user.id
    register_user(user_id)
    
    if message.text == "📨 Get Gmail Task":
        bot.send_message(message.chat.id, "Select your task option:", reply_markup=task_options_menu())
    elif message.text == "💰 Wallet":
        try:
            conn = get_db_connection()
            user = conn.execute("SELECT balance, completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
            conn.close()
            bot.send_message(message.chat.id, f"💳 **Aapka Wallet Details:**\n\n💰 Total Balance: ₹{user['balance']}\n✅ Completed Single Tasks: {user['completed_single_tasks']}")
        except:
            bot.send_message(message.chat.id, "❌ System busy.")
    elif message.text == "👥 Invite & Earn":
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={user_id}"
        bot.send_message(message.chat.id, f"👥 **Invite & Earn Program:**\n\nPer Invite aapko **₹1** milega.\nAapka unique referral link ye raha:\n\n`{invite_link}`", parse_mode="Markdown")
    elif message.text == "💸 Withdraw":
        try:
            conn = get_db_connection()
            user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
            conn.close()
            if user['balance'] >= 15.0:
                msg = bot.send_message(message.chat.id, "💰 Please send your **UPI ID** for withdrawal:")
                bot.register_next_step_handler(msg, process_withdrawal)
            else:
                bot.send_message(message.chat.id, f"❌ Minimum withdrawal amount **₹15** hai. Aapka current balance **₹{user['balance']}** hai.")
        except:
            pass
    elif message.text == "📚 Help & Tutorial":
        bot.send_message(message.chat.id, "📹 **Help & Tutorial Video:**\n\n[Yahan Admin Video Add Kar Sakta Hai]")

def process_withdrawal(message):
    user_id = message.from_user.id
    upi_id = message.text
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if user['balance'] < 15.0:
            bot.send_message(message.chat.id, "❌ Balance insufficient.")
            conn.close()
            return
        balance_to_withdraw = user['balance']
        conn.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ Request Submitted! ₹{balance_to_withdraw} ka withdrawal process ho raha hai admin panel par.")
        bot.send_message(ADMIN_ID, f"🚨 **NEW WITHDRAWAL** 🚨\n\n👤 User: `{user_id}`\n💰 Amount: ₹{balance_to_withdraw}\n📱 UPI: `{upi_id}`", parse_mode="Markdown")
    except:
        pass

# --- CALLBACK QUERY HANDLERS ---
@bot.callback_query_handler(func=lambda call: True and not call.data.startswith('adm_'))
def handle_callbacks(call):
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    try:
        conn = get_db_connection()
        active_session = conn.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,)).fetchone()

        if call.data == "task_single":
            if active_session:
                bot.answer_callback_query(call.id, "❌ Aapka ek task already chal raha hai!", show_alert=True)
                conn.close()
                return
            task = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 1").fetchone()
            if not task:
                bot.answer_callback_query(call.id, "⚠️ No Gmails Available right now in stock!", show_alert=True)
                conn.close()
                return
            current_time = int(time.time())
            conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, task['id']))
            conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'SINGLE', ?, ?)", (user_id, str(task['id']), current_time))
            conn.commit()
            task_msg = f"📨 **Your Single Gmail Task:**\n\n📧 **Gmail:** `{task['gmail']}`\n🔑 **Password:** `{task['password']}`\n\n⚠️ **Note:** Under 10M submit karein."
            bot.edit_message_text(task_msg, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=task_action_buttons())

        elif call.data == "task_batch":
            if active_session:
                bot.answer_callback_query(call.id, "❌ Aapka ek task already chal raha hai!", show_alert=True)
                conn.close()
                return
            user_data = conn.execute("SELECT completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if user_data['completed_single_tasks'] < 10:
                bot.answer_callback_query(call.id, "❌ Access Denied!", show_alert=True)
                bot.send_message(chat_id, f"🔒 **complete first 10 gmails single mode se!** ({user_data['completed_single_tasks']}/10)")
                conn.close()
                return
            tasks = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 10").fetchall()
            if len(tasks) < 10:
                bot.answer_callback_query(call.id, f"😢 Stock kam hai! (Sirf {len(tasks)} bache hain).", show_alert=True)
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
            bot.edit_message_text(batch_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=task_action_buttons())

        elif call.data == "task_cancel":
            if not active_session:
                conn.close()
                return
            ids = active_session['task_id_list'].split(',')
            for t_id in ids:
                conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(t_id),))
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()
            bot.edit_message_text("❌ Task Cancelled.", chat_id, call.message.message_id)

        elif call.data == "task_done":
            if not active_session:
                conn.close()
                return
            conn.execute("UPDATE sessions SET status = 'DONE_SUBMITTED' WHERE user_id = ?", (user_id,))
            conn.commit()
            msg = bot.send_message(chat_id, "📸 Please **Submit Screenshot** proof:")
            bot.register_next_step_handler(msg, process_screenshot_proof, active_session['task_type'], active_session['task_id_list'])

        conn.close()
    except Exception as e:
        bot.answer_callback_query(call.id, f"⚠️ Error: {e}", show_alert=True)

# --- PROOF VERIFICATION ---
def process_screenshot_proof(message, task_type, task_id_list):
    user_id = message.from_user.id
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Screenshot proof hi chahiye.")
        return
    file_id = message.photo[-1].file_id
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 Approve", callback_data=f"adm_app_{user_id}_{task_type}_{task_id_list}"),
        types.InlineKeyboardButton("🔴 Reject", callback_data=f"adm_rej_{user_id}_{task_id_list}")
    )
    bot.send_photo(ADMIN_ID, file_id, caption=f"🛰️ **NEW PROOF**\n👤 User: `{user_id}`\n🗂️ Type: {task_type}", reply_markup=admin_markup)
    bot.send_message(message.chat.id, "⏳ Proof sent to admin.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('adm_'))
def handle_admin_audit(call):
    if call.from_user.id != ADMIN_ID:
        return
    data_parts = call.data.split('_')
    action = data_parts[1]
    target_user = int(data_parts[2])
    try:
        conn = get_db_connection()
        if action == "app":
            task_type = data_parts[3]
            task_id_list = data_parts[4]
            ids = task_id_list.split(',')
            for t_id in ids:
                conn.execute("UPDATE task_pool SET status = 'COMPLETED' WHERE id = ?", (int(t_id),))
            if task_type == "SINGLE":
                conn.execute("UPDATE users SET balance = balance + 2.0, completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (target_user,))
            else:
                conn.execute("UPDATE users SET balance = balance + 20.0 WHERE user_id = ?", (target_user,))
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (target_user,))
            conn.commit()
            bot.edit_message_caption("🟢 Approved!", call.message.chat.id, call.message.message_id)
            bot.send_message(target_user, f"🎉 Approved!")
        elif action == "rej":
            task_id_list = data_parts[3]
            ids = task_id_list.split(',')
            for t_id in ids:
                conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(t_id),))
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (target_user,))
            conn.commit()
            bot.edit_message_caption("🔴 Rejected!", call.message.chat.id, call.message.message_id)
            bot.send_message(target_user, "❌ Task rejected.")
        conn.close()
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)

# --- START BOT ---
print("🚀 Bot is live...")
bot.infinity_polling()
