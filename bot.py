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
    ''');
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail TEXT,
            password TEXT,
            assigned_to INTEGER DEFAULT NULL,
            assigned_at INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'AVAILABLE'
        )
    ''');
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_type TEXT,
            task_id_list TEXT,
            current_index INTEGER DEFAULT 0,
            submitted_proofs TEXT DEFAULT '',
            started_at INTEGER,
            status TEXT DEFAULT 'PENDING'
        )
    ''');
    
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
        
        # FEATURE 1: Rules ke mutabiq 10m me timeout hone par hi auto-stock me data wapas jayega
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
        types.InlineKeyboardButton("📦 10x Batch Task (Upto ₹20/Gmail)", callback_data="task_batch")
    )
    return markup

def individual_step_buttons(session_id, is_last=False):
    markup = types.InlineKeyboardMarkup(row_width=2)
    done_text = "✅ Done & Submit SS" if not is_last else "🏁 Finish & Submit Batch"
    markup.add(
        types.InlineKeyboardButton(done_text, callback_data=f"stepdone_{session_id}"),
        types.InlineKeyboardButton("❌ Cancel Task", callback_data=f"stepcancel_{session_id}")
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
        "👋 **Welcome! Gmail Task Bot me aapka swagat hai.**\n\n👇 Niche diye gaye buttons se kaam shuru karein aur paise kamayein!", 
        reply_markup=main_menu()
    )

# --- ADMIN COMMAND PANELS ---
@bot.message_handler(commands=['addbalance'])
def admin_add_balance(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/addbalance", "").strip()
        parts = raw_text.split()
        if len(parts) < 2:
            bot.send_message(ADMIN_ID, "❌ **Format:** `/addbalance USER_ID AMOUNT`")
            return
        target_uid = int(parts[0])
        amount = float(parts[1])
        conn = get_db_connection()
        conn.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0.0)", (target_uid,))
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_uid))
        conn.commit()
        new_bal = conn.execute("SELECT balance FROM users WHERE user_id = ?", (target_uid,)).fetchone()['balance']
        conn.close()
        bot.send_message(ADMIN_ID, f"✅ Balance Credited! New: ₹{new_bal}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(commands=['bulkadd'])
def bulk_add_tasks(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/bulkadd", "").strip()
        if not raw_text:
            bot.send_message(ADMIN_ID, "❌ **Format:**\n`/bulkadd`\n`email:pass`")
            return
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
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(commands=['viewstock'])
def admin_view_stock(message):
    if message.from_user.id != ADMIN_ID: return
    conn = get_db_connection()
    stock_tasks = conn.execute("SELECT id, gmail, password FROM task_pool WHERE status = 'AVAILABLE' LIMIT 30").fetchall()
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
        bot.send_message(ADMIN_ID, f"🗑️ Task ID {task_id} manually dropped from DB.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

# --- INTERACTIVE FLOW CONTROLLER (INDIVIDUAL STEP DETECTION) ---
def render_current_subtask(chat_id, session_id):
    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not session:
        conn.close()
        return
        
    ids = session['task_id_list'].split(',')
    current_idx = session['current_index']
    total_tasks = len(ids)
    
    if current_idx >= total_tasks:
        # Pura batch khatam hone par process deployment block
        conn.close()
        deploy_completed_batch_proof(chat_id, session_id)
        return
        
    target_task_id = int(ids[current_idx])
    task = conn.execute("SELECT * FROM task_pool WHERE id = ?", (target_task_id,)).fetchone()
    conn.close()
    
    is_last = (current_idx == total_tasks - 1)
    mode_title = "Single Mode Task" if total_tasks == 1 else f"Bulk Batch Task Progress ({current_idx + 1}/{total_tasks})"
    
    flow_msg = (
        f"🛰️ **{mode_title}** 🛰️\n\n"
        f"📧 **Gmail:** `{task['gmail']}`\n"
        f"🔑 **Password:** `{task['password']}`\n\n"
        f"👉 Gmail login karke details save karein aur niche diye gaye **Done** button par click karke screenshot submit karein!"
    )
    bot.send_message(chat_id, flow_msg, parse_mode="Markdown", reply_markup=individual_step_buttons(session_id, is_last))

# --- REPLY KEYBOARD ACTIONS ---
@bot.message_handler(func=lambda msg: True)
def handle_text_messages(message):
    check_and_release_expired_tasks()
    user_id = message.from_user.id
    register_user(user_id)
    
    if message.text == "📨 Get Gmail Task":
        bot.send_message(message.chat.id, "🗂️ **Select your task option below:**", reply_markup=task_options_menu())
    elif message.text == "💰 Wallet":
        conn = get_db_connection()
        user = conn.execute("SELECT balance, completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        bot.send_message(message.chat.id, f"💳 **Wallet Status:**\n💰 **Balance:** ₹{user['balance']}\n✅ **Completed Tasks:** {user['completed_single_tasks']}")
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
            bot.send_message(message.chat.id, "❌ **Invalid amount ya low balance.**")
            return
        msg = bot.send_message(message.chat.id, "📱 **Ab apni Real UPI ID bhejein:**")
        bot.register_next_step_handler(msg, process_withdrawal_admin_review, amount)
    except:
        bot.send_message(message.chat.id, "❌ Valid number dalein.")

def process_withdrawal_admin_review(message, amount):
    user_id = message.from_user.id
    upi_id = message.text
    conn = get_db_connection()
    user_data = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user_data or user_data['balance'] < amount:
        bot.send_message(message.chat.id, "❌ Low Balance.")
        conn.close()
        return
    # Instant balance lock layer
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
    
    # Direct payout panel delivery to channel
    bot.send_message(WITHDRAW_CHANNEL_ID, f"🚨 **NEW WITHDRAWAL PENDING** 🚨\n👤 User: `{user_id}`\n💵 Amount: ₹{amount}\n📱 UPI: `{upi_id}`", parse_mode="Markdown", reply_markup=wd_markup)

# --- CALLBACK ROUTER LOGIC ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data.startswith('wd_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, amount = parts[1], int(parts[2]), float(parts[3])
        conn = get_db_connection()
        if action == "app":
            bot.edit_message_text(f"🟢 **Approved Payout of ₹{amount}**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"✅ Aapka ₹{amount} ka withdrawal successful transfer ho gaya hai!")
        elif action == "rej":
            # FEATURE Auto Restore on Payout failure
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
            conn.commit()
            bot.edit_message_text(f"🔴 **Rejected Payout! Balance Refunded.**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"❌ Aapka withdrawal reject ho gaya. ₹{amount} wapas wallet me add kar diya gaya hai.")
        conn.close()
        return

    if call.data.startswith('adm_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, session_id = parts[1], int(parts[2]), int(parts[3])
        conn = get_db_connection()
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not session:
            conn.close()
            return
            
        ids = session['task_id_list'].split(',')
        total_count = len(ids)
        
        if action == "app":
            for t_id in ids:
                conn.execute("UPDATE task_pool SET status = 'COMPLETED' WHERE id = ?", (int(t_id),))
            # FEATURE 2: Bulk me poora complete karne par ₹20 ke hisab se calculations
            rate = 15.0 if total_count == 1 else 20.0
            final_reward = rate * total_count
            
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (final_reward, target_user))
            if total_count == 1: conn.execute("UPDATE users SET completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (target_user,))
            conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
            conn.commit()
            bot.edit_message_caption(f"🟢 **Approved! Paid ₹{final_reward} ({total_count} Gmails)**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"🎉 Admin ne aapka task proof approve kar diya! ₹{final_reward} add ho gaye.")
            
        elif action == "rej":
            # FEATURE 1: Rules ke mutabiq reject hone par stock me wapas nahi jayega, database se DELETE ho jayega!
            for t_id in ids:
                conn.execute("DELETE FROM task_pool WHERE id = ?", (int(t_id),))
            conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
            conn.commit()
            bot.edit_message_caption("🔴 **Rejected! Kharab Gmails Permanent Delete Ho Gaye Stock Se.**", chat_id, call.message.message_id)
            bot.send_message(target_user, "❌ Aapka submission proof reject ho gaya kyunki credentials kharab the.")
        conn.close()
        return

    # Task allocation panel handlers
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
        bot.delete_message(chat_id, call.message.message_id)
        render_current_subtask(chat_id, sid)
        
    elif call.data == "task_batch":
        # Check requirement rule
        ud = conn.execute("SELECT completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if ud['completed_single_tasks'] < 10:
            bot.answer_callback_query(call.id, "🔒 Pehle 10 single task complete karein!", show_alert=True)
            conn.close()
            return
        tasks = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 10").fetchall()
        if len(tasks) < 10:
            bot.answer_callback_query(call.id, f"😢 Stock low hai! Sirf {len(tasks)} available.", show_alert=True)
            conn.close()
            return
        current_time = int(time.time())
        t_ids = [str(t['id']) for t in tasks]
        for t in tasks: conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, t['id']))
        cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'BATCH_10', ?, ?)", (user_id, ",".join(t_ids), current_time))
        sid = cursor.lastrowid
        conn.commit()
        conn.close()
        bot.delete_message(chat_id, call.message.message_id)
        render_current_subtask(chat_id, sid)

    elif call.data.startswith('stepcancel_'):
        sid = int(call.data.split('_')[1])
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        if session:
            # Partial cancellation rule application
            ids = session['task_id_list'].split(',')
            curr_idx = session['current_index']
            # FEATURE 2: 3-5 karke beech me chorne par processed elements ka ₹15 karke evaluation panel deploy hoga
            if curr_idx >= 3:
                bot.edit_message_text(f"⚠️ Aapne beech me task cancel kiya! Par aapne {curr_idx} Gmails complete kar liye hain, iska proof admin review par chala gaya hai.", chat_id, call.message.message_id)
                conn.close()
                deploy_partial_batch_proof(chat_id, sid)
                return
            else:
                for t_id in ids:
                    conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(t_id),))
                conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                conn.commit()
                bot.edit_message_text("❌ Task Cancelled Successfully. Stock rolled back.", chat_id, call.message.message_id)
        conn.close()

    elif call.data.startswith('stepdone_'):
        sid = int(call.data.split('_')[1])
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "📸 **Ab is step ka confirmation screenshot image upload karein:**")
        bot.register_next_step_handler(msg, capture_individual_proof_image, sid)
        conn.close()

# --- STEP SCREENSHOT CAPTURE PROCESSOR ---
def capture_individual_proof_image(message, session_id):
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Photo format required! Task flow resetting for current step.")
        render_current_subtask(message.chat.id, session_id)
        return
        
    file_id = message.photo[-1].file_id
    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    
    if not session:
        conn.close()
        return
        
    current_proofs = session['submitted_proofs']
    new_proofs = f"{current_proofs},{file_id}" if current_proofs else file_id
    new_index = session['current_index'] + 1
    
    conn.execute("UPDATE sessions SET current_index = ?, submitted_proofs = ? WHERE id = ?", (new_index, new_proofs, session_id))
    conn.commit()
    conn.close()
    
    # Automate moving forward to next queue object immediately
    render_current_subtask(message.chat.id, session_id)

# --- DIRECT TO CHANNEL PROOF DISPATCHERS ---
def deploy_completed_batch_proof(chat_id, session_id):
    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    
    proof_array = session['submitted_proofs'].split(',')
    media_group = [types.InputMediaPhoto(media=f_id) for f_id in proof_array]
    
    # Pehla element media group text control base banega
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 Approve Set (₹20/Each)", callback_data=f"adm_app_{session['user_id']}_{session_id}"),
        types.InlineKeyboardButton("🔴 Reject & Drop", callback_data=f"adm_rej_{session['user_id']}_{session_id}")
    )
    
    bot.send_message(chat_id, "⏳ **🎉 Batch Completed! Aapke saare screenshot directly verification channel par upload ho rahe hain. Koi limit nahi hai, aap next task turant shuru karein!**")
    
    # Sending full media sheets straight to validation channels
    bot.send_media_group(GMAIL_CHANNEL_ID, media_group)
    bot.send_message(
        GMAIL_CHANNEL_ID,
        f"🛰️ **FULL 10/10 BATCH SUBMISSION DETECTED** 🛰️\n\n👤 User ID: `{session['user_id']}`\n📈 Rate: **₹20/Gmail Eligible**\n📦 Total Items: 10\n\nReview & Deploy Action Panel:",
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )

def deploy_partial_batch_proof(chat_id, session_id):
    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    
    proof_array = session['submitted_proofs'].split(',')
    media_group = [types.InputMediaPhoto(media=f_id) for f_id in proof_array]
    completed_count = len(proof_array)
    
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 Approve Partial (₹15/Each)", callback_data=f"adm_app_{session['user_id']}_{session_id}"),
        types.InlineKeyboardButton("🔴 Reject & Drop", callback_data=f"adm_rej_{session['user_id']}_{session_id}")
    )
    
    bot.send_media_group(GMAIL_CHANNEL_ID, media_group)
    bot.send_message(
        GMAIL_CHANNEL_ID,
        f"⚠️ **PARTIAL BATCH SUBMISSION DETECTED** ⚠️\n\n👤 User ID: `{session['user_id']}`\n📈 Rate: **₹15/Gmail Tier Applied**\n📦 Processed Items: {completed_count}/10\n\nReview & Deploy Action Panel:",
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )

# --- START BOT ENGINE ---
print("🚀 Automation Core Engine deployed with non-stop task capabilities...")
bot.infinity_polling()
