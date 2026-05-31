import telebot
import sqlite3
import time
import random
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '7990556564:AAFYUQrYcQ7UmwbmFdjPShBFk_kLVYepRpA'
ADMIN_ID = 8031127296

# Channel Chat IDs
GMAIL_CHANNEL_ID = -1003955255909
WITHDRAW_CHANNEL_ID = -1004208044139

# 📢 REQ CHANNELS SET AS PER USER DEMAND
REQUIRED_CHANNELS = ["@Raka_Works", "@RakaXproof", "@BilibiliWorks"] 

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
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

# --- CHANNEL CHECKER LOGIC ---
def is_user_joined_all(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False 
    return True

def force_join_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Join @Raka_Works", url=f"https://t.me/{REQUIRED_CHANNELS[0].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @RakaXproof", url=f"https://t.me/{REQUIRED_CHANNELS[1].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @BilibiliWorks", url=f"https://t.me/{REQUIRED_CHANNELS[2].replace('@','')}"),
        types.InlineKeyboardButton("✅ Joined", callback_data="verify_channels")
    )
    return markup

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
                    bot.send_message(referrer_id, "🎉 **Alert! Aapke link se koi join hua hai. You got ₹1!** 💸")
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
        
        cursor.execute("SELECT id, user_id, task_id_list FROM sessions WHERE started_at < ? AND status = 'PENDING'", (expiry_limit,))
        expired_sessions = cursor.fetchall()
        
        for session in expired_sessions:
            sid = session['id']
            uid = session['user_id']
            if session['task_id_list']:
                ids = session['task_id_list'].split(',')
                for t_id in ids:
                    cursor.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(t_id),))
            
            cursor.execute("DELETE FROM sessions WHERE id = ?", (sid,))
            try:
                bot.send_message(uid, "⏰ **Time Out!** Aapne 10 minute me task submit nahi kiya, isliye task automatically **Cancel** ho gaya hai aur stock me wapas chala gaya hai. ❌")
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
        types.InlineKeyboardButton("📨 1 Gmail Task (₹15)", callback_data="task_single"),
        types.InlineKeyboardButton("📦 0/10 Gmail Task Bulk", callback_data="task_batch")
    )
    return markup

def bulk_line_action_buttons(session_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Done & Submit Proof", callback_data=f"done_{session_id}"),
        types.InlineKeyboardButton("❌ Cancel Batch", callback_data=f"cancel_{session_id}")
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
    
    if not is_user_joined_all(user_id):
        bot.send_message(
            message.chat.id, 
            "⚠️ **Aapko bot use karne ke liye hamare 3 Channels join karne honge!**\nNiche diye channels join karein aur 'Joined' par click karein.",
            reply_markup=force_join_keyboard()
        )
        return

    bot.send_message(
        message.chat.id, 
        "👋 **Welcome! Gmail Task Bot me aapka swagat hai.**\n\n👇 Niche diye gaye buttons se kaam shuru karein aur paise kamayein!", 
        reply_markup=main_menu()
    )

# --- ADMIN EXCLUSIVE CONTROLS ---
@bot.message_handler(commands=['addbalance'])
def admin_add_balance(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/addbalance", "").strip()
        parts = raw_text.split()
        if len(parts) < 2: return
        target_uid = int(parts[0])
        amount = float(parts[1])
        conn = get_db_connection()
        conn.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0.0)", (target_uid,))
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_uid))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, "✅ Balance Credited Successfully!")
    except Exception as e: bot.send_message(ADMIN_ID, f"Error: {e}")

@bot.message_handler(commands=['bulkadd'])
def bulk_add_tasks(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/bulkadd", "").strip()
        lines = raw_text.split("\n")
        success_count = 0
        conn = get_db_connection()
        for line in lines:
            if ":" in line:
                gmail, password = line.strip().split(":", 1)
                conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
                success_count += 1
        conn.commit()
        total_stock = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        conn.close()
        bot.send_message(ADMIN_ID, f"✅ Bulk Added: {success_count} | Live Stock: {total_stock}")
    except Exception as e: bot.send_message(ADMIN_ID, f"Error: {e}")

@bot.message_handler(commands=['viewstock'])
def admin_view_stock(message):
    if message.from_user.id != ADMIN_ID: return
    conn = get_db_connection()
    stock_tasks = conn.execute("SELECT id, gmail FROM task_pool WHERE status = 'AVAILABLE' LIMIT 30").fetchall()
    conn.close()
    if not stock_tasks:
        bot.send_message(ADMIN_ID, "📦 Stock Empty!")
        return
    stock_text = "🔥 **LIVE GMAIL STOCK** 🔥\n\n"
    for task in stock_tasks:
        stock_text += f"🆔 `ID: {task['id']}` -> `{task['gmail']}`\n"
    bot.send_message(ADMIN_ID, stock_text, parse_mode="Markdown")

@bot.message_handler(commands=['deletetask'])
def admin_delete_task(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        task_id = int(message.text.replace("/deletetask", "").strip())
        conn = get_db_connection()
        conn.execute("DELETE FROM task_pool WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, f"🗑️ Task ID {task_id} manually dropped.")
    except Exception as e: bot.send_message(ADMIN_ID, f"Error: {e}")

# --- REPLY KEYBOARD INTERACTION SYSTEM ---
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    check_and_release_expired_tasks()
    user_id = message.from_user.id
    register_user(user_id)
    
    if not is_user_joined_all(user_id):
        bot.send_message(
            message.chat.id, 
            "❌ **Access Denied! Aapne hamare channels left kar diye hain.** Re-join karne ke liye niche click karein.",
            reply_markup=force_join_keyboard()
        )
        return
        
    if message.text == "📨 Get Gmail Task":
        bot.send_message(message.chat.id, "🗂️ **Select your task option below:**", reply_markup=task_options_menu())
    elif message.text == "💰 Wallet":
        conn = get_db_connection()
        user = conn.execute("SELECT balance, completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        bot.send_message(message.chat.id, f"💳 **\"Wallet Status:\"**\n💰 **\"Balance:\"** ₹{user['balance']}\n✅ **\"Completed Tasks:\"** {user['completed_single_tasks']}")
    elif message.text == "👥 Invite & Earn":
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={user_id}"
        bot.send_message(message.chat.id, f"👥 **Invite Program:** Per Invite ₹1.\n🔗 Link: `{invite_link}`", parse_mode="Markdown")
    elif message.text == "💸 Withdraw":
        conn = get_db_connection()
        user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if user['balance'] >= 15.0:
            msg = bot.send_message(message.chat.id, f"💰 Available: ₹{user['balance']}\n🔢 **Kitna amount withdraw karna chahte hain?**")
            bot.register_next_step_handler(msg, ask_upi_id)
        else:
            bot.send_message(message.chat.id, f"❌ **Minimum withdrawal amount ₹15 hai.**")

def ask_upi_id(message):
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        conn = get_db_connection()
        user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if amount < 15.0 or amount > user['balance']:
            bot.send_message(message.chat.id, "❌ **Invalid amount ya balance kam hai.**")
            return
        msg = bot.send_message(message.chat.id, "📱 **Ab apni Real UPI ID bhejein:**")
        bot.register_next_step_handler(msg, process_withdrawal_admin_review, amount)
    except:
        bot.send_message(message.chat.id, "❌ Sahi value input karein.")

def process_withdrawal_admin_review(message, amount):
    user_id = message.from_user.id
    upi_id = message.text
    conn = get_db_connection()
    user_data = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user_data or user_data['balance'] < amount:
        bot.send_message(message.chat.id, "❌ Low Balance.")
        conn.close()
        return
        
    conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    
    wd_markup = types.InlineKeyboardMarkup()
    wd_markup.add(
        types.InlineKeyboardButton("🟢 Approve Payout", callback_data=f"wd_app_{user_id}_{amount}"),
        types.InlineKeyboardButton("🔴 Reject Payout", callback_data=f"wd_rej_{user_id}_{amount}")
    )
    success_text = f"✅ **\"Withdrawal Request Submitted!\"**\n\n💰 **\"Amount:\"** ₹{amount}\n📱 **\"UPI ID:\"** {upi_id}\n\n⚠️ **\"Payment Under 24 Hours\"**"
    bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
    
    bot.send_message(WITHDRAW_CHANNEL_ID, f"🚨 **NEW WITHDRAWAL PENDING** 🚨\n👤 User: `{user_id}`\n💵 Amount: ₹{amount}\n📱 UPI: `{upi_id}`", parse_mode="Markdown", reply_markup=wd_markup)

# --- CALLBACK ROUTER HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data == "verify_channels":
        if is_user_joined_all(user_id):
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "🎉 **Channels verified successfully! All options unlocked.**", reply_markup=main_menu())
            
            u_info = call.from_user
            alert_msg = (
                f"👤 **NEW USER JOINED CHANNELS** 👤\n\n"
                f"🆔 **User ID:** `{u_info.id}`\n"
                f"Base Name: {u_info.first_name}\n"
                f"Username: @{u_info.username if u_info.username else 'N/A'}\n"
                f"⚡ **Status:** Active Member"
            )
            bot.send_message(ADMIN_ID, alert_msg, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Aapne saare 3 channels join nahi kiye hain!", show_alert=True)
        return

    if not is_user_joined_all(user_id) and call.data != "verify_channels":
        bot.answer_callback_query(call.id, "❌ Pehle channels join karein!", show_alert=True)
        return

    if call.data.startswith('wd_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, amount = parts[1], int(parts[2]), float(parts[3])
        conn = get_db_connection()
        if action == "app":
            bot.edit_message_text(f"🟢 **Approved Payout of ₹{amount}**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"✅ Aapka ₹{amount} ka withdrawal approved ho gaya hai!")
        elif action == "rej":
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
            conn.commit()
            bot.edit_message_text(f"🔴 **Rejected Payout! Balance Refunded.**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"❌ Aapka withdrawal reject ho gaya. Balance safely refund kar diya gaya.")
        conn.close()
        return

    if call.data.startswith('adm_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, session_id, count_override = parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        conn = get_db_connection()
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        
        if action == "app":
            if session:
                ids = session['task_id_list'].split(',')
                for t_id in ids:
                    conn.execute("UPDATE task_pool SET status = 'COMPLETED' WHERE id = ?", (int(t_id),))
            
            rate = 20.0 if count_override >= 10 else 15.0
            final_reward = rate * count_override
            
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (final_reward, target_user))
            conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
            conn.commit()
            bot.edit_message_caption(f"🟢 **Approved! Paid ₹{final_reward} ({count_override} Gmails verified at ₹{int(rate)}/ea)**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"🎉 Admin ne aapka proof approve kar diya! ₹{final_reward} add ho gaye.")
            
        elif action == "rej":
            if session:
                ids = session['task_id_list'].split(',')
                for t_id in ids:
                    conn.execute("DELETE FROM task_pool WHERE id = ?", (int(t_id),))
            conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
            conn.commit()
            bot.edit_message_caption("🔴 **Rejected & Destroyed From Stock!**", chat_id, call.message.message_id)
            bot.send_message(target_user, "❌ Aapka submission proof reject ho gaya. Credentials pool se drop ho gaye hain.")
        conn.close()
        return

    conn = get_db_connection()
    if call.data == "task_single":
        task = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 1").fetchone()
        if not task:
            bot.answer_callback_query(call.id, "⚠️ Stock Empty!", show_alert=True)
            conn.close()
            return
        current_time = int(time.time())
        conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, task['id']))
        cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'SINGLE', ?, ?)", (user_id, str(task['id']), current_time))
        sid = cursor.lastrowid
        conn.commit()
        conn.close()
        
        task_msg = f"📨 **Your Single Gmail Task:**\n\n📧 **Gmail:** `{task['gmail']}`\n🔑 **Password:** `{task['password']}`"
        bot.send_message(chat_id, task_msg, parse_mode="Markdown", reply_markup=bulk_line_action_buttons(sid))

    elif call.data == "task_batch":
        ud = conn.execute("SELECT completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if ud['completed_single_tasks'] < 10:
            bot.answer_callback_query(call.id, "pehle 10 single task complete karein!", show_alert=True)
            conn.close()
            return
        tasks = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 10").fetchall()
        if len(tasks) < 10:
            bot.answer_callback_query(call.id, f"😢 Stock low hai! Sirf {len(tasks)} items bache hain.", show_alert=True)
            conn.close()
            return
            
        current_time = int(time.time())
        t_ids = [str(t['id']) for t in tasks]
        for t in tasks: 
            conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, t['id']))
        
        cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'BATCH_10', ?, ?)", (user_id, ",".join(t_ids), current_time))
        sid = cursor.lastrowid
        conn.commit()
        conn.close()
        
        bulk_text = "📦 **0/10 GMAIL BULK TASK LIST** 📦\n\nNiche diye gaye saare gmails line se setup karein:\n\n"
        for index, t in enumerate(tasks, 1):
            bulk_text += f"{index}️⃣. 📧 `{t['gmail']}` | 🔑 `{t['password']}`\n"
        bulk_text += "\n⚠️ **Note:** Complete tasks and click action below."
        
        bot.send_message(chat_id, bulk_text, parse_mode="Markdown", reply_markup=bulk_line_action_buttons(sid))

    elif call.data.startswith("cancel_"):
        sid = int(call.data.split('_')[1])
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        if session:
            ids = session['task_id_list'].split(',')
            for t_id in ids:
                conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(t_id),))
            conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
            conn.commit()
        bot.edit_message_text("❌ Task Cancelled. Stock restored.", chat_id, call.message.message_id)
        conn.close()

    elif call.data.startswith("done_"):
        sid = int(call.data.split('_')[1])
        msg = bot.send_message(chat_id, "📸 **Aapne jitne bhi gmails banaye hain (1-10), unka composite proof screenshot image send karein:**")
        bot.register_next_step_handler(msg, process_final_channel_proof, sid)
        conn.close()

# --- CHANNEL PROOF ROUTER MANAGEMENT ---
def process_final_channel_proof(message, session_id):
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Proof structure missing! Photo input required. Naya task le lijiye.")
        return
        
    file_id = message.photo[-1].file_id
    user_id = message.from_user.id
    
    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    
    if not session: return
    ids_count = len(session['task_id_list'].split(','))
    
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 Approve All 10 (₹20/ea)", callback_data=f"adm_app_{user_id}_{session_id}_10"),
        types.InlineKeyboardButton("🟡 Approve Partial 5 (₹15/ea)", callback_data=f"adm_app_{user_id}_{session_id}_5"),
        types.InlineKeyboardButton("🔴 Reject & Delete", callback_data=f"adm_rej_{user_id}_{session_id}_0")
    )
    
    bot.send_photo(
        GMAIL_CHANNEL_ID,
        file_id,
        caption=f"🛰️ **NEW PROGRESS TASK VALIDATION** 🛰️\n\n👤 **User ID:** `{user_id}`\n🗂️ **Batch Type:** {session['task_type']}\n📦 **Assigned Items:** {ids_count} Gmails\n\nAdmin review details manually:",
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )
    bot.send_message(message.chat.id, "⏳ **Aapka screenshot proof channels validation panel me bhej diya gaya hai! No Limits system active hai, aap turant NEXT task shuru kar sakte hain.** 🎉")

# --- START BOT ENGINE ---
print("🚀 Security Channel Verification Core online with updated Raka channels...")
bot.infinity_polling()
