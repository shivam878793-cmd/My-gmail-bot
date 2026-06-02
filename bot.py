import telebot
import sqlite3
import time
import random
import threading  # Multi-threaded background process support execution maps
from telebot import types

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 1: MASTER CONFIGURATION & SYSTEM GLOBALS
# ──────────────────────────────────────────────────────────────────────

API_TOKEN = '7990556564:AAFYUQrYcQ7UmwbmFdjPShBFk_kLVYepRpA'
ADMIN_ID = 8031127296

# Telegram Logging Channel Chat IDs Directional Path Mapping
GMAIL_CHANNEL_ID = -1003955255909
WITHDRAW_CHANNEL_ID = -1004208044139

# Mandatory Verification Channels List As Per User Explicit Demand
REQUIRED_CHANNELS = ["@Raka_Works", "@RakaXproof", "@BilibiliWorks"] 

bot = telebot.TeleBot(API_TOKEN)

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 2: DATABASE INITIALIZATION & ARCHITECTURE (SQLITE3)
# ──────────────────────────────────────────────────────────────────────

def get_db_connection():
    """Establishes a stable and secure connection to the local database file."""
    conn = sqlite3.connect('gmail_bot.db', timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all essential relational schemas required for the application core runtime state tracking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    
    # Core system structural design database initialization execution parameters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            referred_by INTEGER,
            completed_single_tasks INTEGER DEFAULT 0,
            cancel_count INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Static master parameter initialization
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tutorial', '📹 **Help & Tutorial Video:**\\n\\n[No video link set yet by admin. Use /sethelp to update]')")
    
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Database Initialization Error: {e}")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 3: SECURITY MIDDLEWARE & ACCOUNT MEMBERSHIP CHECKER
# ──────────────────────────────────────────────────────────────────────

def is_user_joined_all(user_id):
    """Intercepts and performs strict validation routines against the external channels infrastructure."""
    if user_id == ADMIN_ID:
        return True
    
    # BAN CONTROLLER INTERCEPT LAYER
    conn = get_db_connection()
    u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if u_chk and u_chk['is_banned'] == 1:
        return False
        
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked', 'bad_request']:
                return False
        except Exception:
            return False 
    return True

def force_join_keyboard():
    """Generates a clean inline menu mapping exact link coordinates to the mandatory channels network."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Join @Raka_Works", url=f"https://t.me/{REQUIRED_CHANNELS[0].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @RakaXproof", url=f"https://t.me/{REQUIRED_CHANNELS[1].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @BilibiliWorks", url=f"https://t.me/{REQUIRED_CHANNELS[2].replace('@','')}"),
        types.InlineKeyboardButton("✅ Joined (Verify Account)", callback_data="verify_channels")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 4: TRANSACTIONS & SYSTEM HELPER UTILITIES
# ──────────────────────────────────────────────────────────────────────

def register_user(user_id, referrer_id=None):
    """Processes user signup entries and hooks referral calculations automatically into the datastore space."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, referrer_id))
            if referrer_id:
                cursor.execute("UPDATE users SET balance = balance + 1.0 WHERE user_id = ?", (referrer_id,))
                try:
                    bot.send_message(referrer_id, "🔔 **REFERRAL ALERT!**\n\n🎉 **Aapke link se ek naye member ne bot join kiya hai!**\n💰 **Aapko milta hai: +₹1.00 Cash reward direct wallet me!** 💸")
                except:
                    pass
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error in register_user: {e}")

def check_and_release_expired_tasks():
    """Scans structural tracking records for dead lock objects and releases stale elements safely back into pool."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_time = int(time.time())
        
        # Timer mapped to 60 minutes structural track intervals
        expiry_limit = current_time - 3600
        
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
                bot.send_message(uid, "⏰ **TIME OUT ALERT!**\n\n⚠️ Aapne **60 minute (1 ghanta)** ke andar task poora karke submit nahi kiya.\n❌ Isliye aapka task automatically **Cancel** karke wapas stock pool me bhej diya gaya hai!")
            except:
                pass
                
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error in expiry checker: {e}")

# 🚀 HIGH PERFORMANCE MEMORY-BASED NON-BLOCKING ASYNC BROADCAST MOTOR TRIPPERS
def broadcast_stock_worker(added_count, current_total):
    """Internal sub-thread loops logic mapped to isolate connections while executing large loops safely."""
    try:
        conn = get_db_connection()
        user_rows = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        conn.close()
        
        user_list = [row['user_id'] for row in user_rows]
        
        alert_text = (
            "🔥 **FRESH GMAIL STOCK ADDED!** 🔥\n\n"
            f"📨 **Admin ne abhi naye {added_count} Gmail Tasks update kiye hain!**\n"
            f"📦 **Total Live Stock Available:** `{current_total}` Gmails\n\n"
            "💰 Jaldi aao, apna task claim karo aur unlimited earning shuru karo yrr! 🚀"
        )
        
        count = 0
        for uid in user_list:
            try:
                bot.send_message(chat_id=uid, text=alert_text, parse_mode="Markdown")
                count += 1
                if count % 20 == 0:
                    time.sleep(1.0)
                else:
                    time.sleep(0.04)
            except Exception:
                continue
    except Exception as e:
        print(f"Background async stock alert processor failure handler logs: {e}")

def auto_stock_broadcast_alert(added_count, current_total):
    """Fires up a non-interfering subthread mapping structural parameters instantly outside runtime tracks."""
    thr = threading.Thread(target=broadcast_stock_worker, args=(added_count, current_total))
    thr.start()

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 5: HIGH-DENSITY PHOTO INTERCEPTOR SYSTEM (19649.jpg RESOLVED)
# ──────────────────────────────────────────────────────────────────────

def process_final_channel_proof(message, session_id):
    """Direct processing unit mapping screenshot file identifiers into validation pipeline logs."""
    if not message.photo:
        bot.send_message(message.chat.id, "❌ **SUBMISSION ERROR!**\n\n⚠️ Proof verification ke liye sirf Photo/Screenshot format hi bhejni hogi. Process reset.")
        return
        
    file_id = message.photo[-1].file_id
    user_id = message.from_user.id
    
    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    
    if not session: 
        bot.send_message(message.chat.id, "❌ **SESSION ERROR!** Task record expired or invalid.")
        return
        
    ids_count = len(session['task_id_list'].split(','))
    
    if session['task_type'] == 'BATCH_ROW':
        task_label = "📦 [10x BULK MODE TASK PROOF]"
    else:
        task_label = "📨 [SINGLE MODE TASK PROOF]"
    
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("🟢 Approve at ₹15/Gmail", callback_data=f"adm_rate15_{user_id}_{session_id}_{ids_count}"),
        types.InlineKeyboardButton("🟡 Approve at ₹20/Gmail", callback_data=f"adm_rate20_{user_id}_{session_id}_{ids_count}"),
        types.InlineKeyboardButton("🔴 Reject & Delete", callback_data=f"adm_rej_{user_id}_{session_id}_0")
    )
    
    bot.send_photo(
        GMAIL_CHANNEL_ID,
        file_id,
        caption=f"🛰️ **NEW PROGRESS TASK VALIDATION** 🛰️\n\n📋 **TASK TYPE:** `{task_label}`\n👤 **User ID:** `{user_id}`\n📦 **Assigned Items:** {ids_count} Gmail(s)\n\nAdmin select correct rate button from panel below to verify:",
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )
    bot.send_message(message.chat.id, "⏳ **Proof uploaded successfully! Aapka screenshot direct audit channel validation panel me bhej diya gaya hai. Next task turant shuru kar sakte hain!** 🎉")

@bot.message_handler(content_types=['photo'])
def catch_global_photo_proofs(message):
    """Intercepts photo packets immediately to avoid collision with standard text handler loops."""
    user_id = message.from_user.id
    
    # Check ban status
    conn = get_db_connection()
    u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if u_chk and u_chk['is_banned'] == 1:
        bot.send_message(message.chat.id, "❌ **Aapka account is bot me Banned hai!**")
        return

    if not is_user_joined_all(user_id):
        bot.send_message(message.chat.id, "❌ Channels verification missing!")
        return

    conn = get_db_connection()
    session = conn.execute("SELECT * FROM sessions WHERE user_id = ? AND status = 'PENDING' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    if session:
        process_final_channel_proof(message, session['id'])
    else:
        bot.send_message(message.chat.id, "❌ **SUBMISSION DENIED!**\n\nAapka koi bhi active locked task background pool me nahi mila. Pehle task uthayein!")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 6: INTERFACE GRAPHICS & LAYOUT KEYBOARDS MAPS
# ──────────────────────────────────────────────────────────────────────

def main_menu():
    """Generates the absolute standard master grid mapping required fields directly inside the device frame matrix."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📨 Get Gmail Task")
    btn2 = types.KeyboardButton("💰 Wallet")
    btn3 = types.KeyboardButton("👥 Invite & Earn")
    btn4 = types.KeyboardButton("💸 Withdraw")
    btn5 = types.KeyboardButton("📚 Help & Tutorial")
    btn6 = types.KeyboardButton("☎️ Contact Owner & Help") 
    
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    markup.add(btn6)
    return markup

def task_options_menu():
    """Generates the inline task router module containing single and bulk selection layouts."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📨 1 Gmail Task (₹15)", callback_data="task_single"),
        types.InlineKeyboardButton("📦 10x Bulk Gmail Task (₹20/ea)", callback_data="task_batch")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 7: ROUTING LOGIC & GATEWAY GATEKEEPERS
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_cmd(message):
    """Processes entry checkpoints and handles user profile setups."""
    user_id = message.from_user.id
    
    # Anti-ban intercept check
    conn = get_db_connection()
    u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if u_chk and u_chk['is_banned'] == 1:
        bot.send_message(message.chat.id, "❌ **Aapka account admin dwara permanently block/ban kar diya gaya hai.**")
        return
        
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
            "⚠️ **MANDATORY CHANNELS JOIN REQUIRED!**\n\n🚀 Bot ko activate karne ke liye aapko hamare **3 Channels** join karna zaroori hai.\n\n👇 Niche diye gaye buttons se jaldi join karein aur phir **Joined** button dabaayein!",
            reply_markup=force_join_keyboard()
        )
        return

    bot.send_message(
        message.chat.id, 
        "👋 **WELCOME TO GMAIL TASK BOT!**\n\n⚡ Yahan aap daily simple Gmail create karne ka kaam karke bohot achhi earning kar sakte hain.\n\n👇 Niche diye buttons se apna kaam shuru karein aur paise kamayein!", 
        reply_markup=main_menu()
    )

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 8: CORE ADMIN CONTROLS & SECURITY MASTER ARRAYS
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['ban'])
def admin_manual_ban(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            bot.send_message(ADMIN_ID, "❌ **Format:** `/ban USER_ID`")
            return
        target_uid = int(parts[1])
        conn = get_db_connection()
        conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (target_uid,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, f"🚫 **User `{target_uid}` has been Banned successfully!**")
        try: bot.send_message(target_uid, "❌ **Aapko admin ne bot se ban kar diya hai.**")
        except: pass
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(commands=['unban'])
def admin_manual_unban(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            bot.send_message(ADMIN_ID, "❌ **Format:** `/unban USER_ID`")
            return
        target_uid = int(parts[1])
        conn = get_db_connection()
        conn.execute("UPDATE users SET is_banned = 0, cancel_count = 0 WHERE user_id = ?", (target_uid,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, f"🟢 **User `{target_uid}` has been Unbanned successfully!**")
        try: bot.send_message(target_uid, f"🎉 **Aapka account unban ho gaya hai!**", reply_markup=main_menu())
        except: pass
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Error: {e}")

@bot.message_handler(commands=['addbalance'])
def admin_add_balance(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/addbalance", "").strip()
        parts = raw_text.split()
        if len(parts) < 2:
            bot.send_message(ADMIN_ID, "❌ **Sahi Format:** `/addbalance USER_ID AMOUNT`")
            return
        target_uid = int(parts[0])
        amount = float(parts[1])
        conn = get_db_connection()
        conn.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0.0)", (target_uid,))
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_uid))
        conn.commit()
        new_bal = conn.execute("SELECT balance FROM users WHERE user_id = ?", (target_uid,)).fetchone()['balance']
        conn.close()
        bot.send_message(ADMIN_ID, f"✅ **Balance Added Successfully!**\n👤 User: `{target_uid}`\n💰 New Balance: ₹{new_bal}")
        try:
            bot.send_message(target_uid, f"🎁 **BONUS RECEIVED!**\n\nAdmin ne aapke wallet me **Extra ₹{amount}** credit kiye hain! 🎉\n💰 **Current Balance:** ₹{new_bal}")
        except: pass
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Error:** {e}")

@bot.message_handler(commands=['addtask'])
def add_task_via_telegram(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/addtask", "").strip()
        if not raw_text or ":" not in raw_text:
            bot.send_message(ADMIN_ID, "❌ **Format:** `/addtask username@gmail.com:password`")
            return
        gmail, password = raw_text.split(":", 1)
        conn = get_db_connection()
        conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
        conn.commit()
        count = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        conn.close()
        
        bot.send_message(ADMIN_ID, f"✅ **Single Task Added Successfully!**\n📦 Current Available Stock: {count} Gmails\n📢 *All users background alert maps processed safely!*")
        
        auto_stock_broadcast_alert(1, count)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Error:** {e}")

@bot.message_handler(commands=['bulkadd'])
def bulk_add_tasks(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/bulkadd", "").strip()
        if not raw_text:
            bot.send_message(ADMIN_ID, "❌ **Format:**\n\n`/bulkadd`\n`email1:pass1`\n`email2:pass2`")
            return
        lines = raw_text.split("\n")
        success_count = 0
        conn = get_db_connection()
        for line in lines:
            if ":" in line:
                try:
                    gmail, password = line.strip().split(":", 1)
                    conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
                    success_count += 1
                except: pass
        conn.commit()
        total_stock = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        conn.close()
        
        bot.send_message(ADMIN_ID, f"📦 **Bulk Import Status:**\n✅ Added: {success_count}\n🔥 Total Live Stock: {total_stock}\n📢 *All users background threads executed smoothly!*")
        
        if success_count > 0:
            auto_stock_broadcast_alert(success_count, total_stock)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Bulk Add Error:** {e}")

@bot.message_handler(commands=['viewtask'])
def admin_view_stock_fixed(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        conn = get_db_connection()
        stock_tasks = conn.execute("SELECT id, gmail, password FROM task_pool WHERE status = 'AVAILABLE' ORDER BY id ASC LIMIT 30").fetchall()
        total_available = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        conn.close()
        
        if not stock_tasks:
            bot.send_message(ADMIN_ID, "📦 **Stock Empty Hai!** Database pool me koi bhi live task nahi mila.")
            return
            
        stock_text = f"🔥 **LIVE AVAILABLE STOCK LIST (Total: {total_available})** 🔥\n\n"
        for task in stock_tasks:
            stock_text += f"🆔 `ID: {task['id']}`\n📧 `{task['gmail']}`\n🔑 `{task['password']}`\n───────────────────\n"
        if total_available > 30:
            stock_text += f"\n*⚠️ Note: Pehle inko clear/delete karein baki dekhne ke liye.*"
        bot.send_message(ADMIN_ID, stock_text, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **View Stock Error:** {e}")

@bot.message_handler(commands=['deletetask'])
def admin_delete_task(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        task_id = message.text.replace("/deletetask", "").strip()
        if not task_id or not task_id.isdigit():
            bot.send_message(ADMIN_ID, "❌ **Sahi Format:** `/deletetask TASK_ID`")
            return
        task_id = int(task_id)
        conn = get_db_connection()
        task_check = conn.execute("SELECT * FROM task_pool WHERE id = ? AND status = 'AVAILABLE'", (task_id,)).fetchone()
        if not task_check:
            bot.send_message(ADMIN_ID, f"❌ **Task ID `{task_id}` Live Stock me nahi mili.**")
            conn.close()
            return
        conn.execute("DELETE FROM task_pool WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, f"🗑️ **Stock Se Deleted!**\n🆔 Task ID: `{task_id}` has been dropped from live pool.")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Delete Task Error:** {e}")

@bot.message_handler(commands=['edittask'])
def admin_edit_task(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_text = message.text.replace("/edittask", "").strip()
        parts = raw_text.split(None, 1)
        if len(parts) < 2 or ":" not in parts[1]:
            bot.send_message(ADMIN_ID, "❌ **Format:** `/edittask TASK_ID new_email@gmail.com:new_password`")
            return
        task_id = int(parts[0])
        new_gmail, new_password = parts[1].strip().split(":", 1)
        conn = get_db_connection()
        conn.execute("UPDATE task_pool SET gmail = ?, password = ? WHERE id = ?", (new_gmail.strip(), new_password.strip(), task_id))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, f"📝 **Task ID `{task_id}` details updated successfully in database.**")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Edit Task Error:** {e}")

@bot.message_handler(commands=['sethelp'])
def admin_set_help_tutorial(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_content = message.text.replace("/sethelp", "").strip()
        if not new_content:
            bot.send_message(ADMIN_ID, "❌ **Format:** `/sethelp Text or custom tutorial link strings`")
            return
        conn = get_db_connection()
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('tutorial', ?)", (new_content,))
        conn.commit()
        conn.close()
        bot.send_message(ADMIN_ID, "✅ **Help & Tutorial message updated in database successfully!**")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Set Help Error:** {e}")

# --- FIXED HIGH PERFORMANCE ANTI-FLOOD MANUAL BROADCAST CORE ---
@bot.message_handler(commands=['broadcast'])
def admin_broadcast_flexible(message):
    if message.from_user.id != ADMIN_ID: return
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        bot.send_message(ADMIN_ID, "❌ **Format:** `/broadcast Write any global message here`")
        return
    try:
        conn = get_db_connection()
        users = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        conn.close()
        
        count = 0
        failed_count = 0
        
        status_msg = bot.send_message(ADMIN_ID, f"📢 **Broadcast Shuru Ho Gaya Hai...**\nTotal Users in DB: {len(users)}")
        
        for u in users:
            try:
                bot.send_message(chat_id=u['user_id'], text=text_to_send, disable_web_page_preview=False)
                count += 1
                
                if count % 20 == 0:
                    time.sleep(1.0)
                else:
                    time.sleep(0.05)
                    
            except telebot.apihelper.ApiTelegramException:
                failed_count += 1
                continue
            except Exception:
                failed_count += 1
                continue
                
        bot.edit_message_text(
            chat_id=ADMIN_ID,
            message_id=status_msg.message_id,
            text=f"📢 **Broadcast Complete Successfully!**\n\n✅ **Delivered To:** `{count}` users\n❌ **Failed/Blocked:** `{failed_count}` users",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Broadcast Engine Failure:** {e}")

@bot.message_handler(commands=['checkuser'])
def admin_check_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_uid = message.text.replace("/checkuser", "").strip()
        if not target_uid or not target_uid.isdigit(): return
        target_uid = int(target_uid)
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (target_uid,)).fetchone()
        conn.close()
        if user:
            bot.send_message(ADMIN_ID, f"🔍 **User Info:**\n👤 ID: `{target_uid}`\n💰 Balance: ₹{user['balance']}\n✅ Completed: {user['completed_single_tasks']}\n⚠️ Cancel Rows: {user['cancel_count']}\n🚫 Ban Status: {user['is_banned']}")
    except Exception as e: pass

# ──────────────────────────────────────────────────────────────────────
# 🛰 *SECTION 9: TEXT LOGIC CONTROLLER AND RESOLUTION ROUTERS*
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_text_messages(message):
    """Monitors standard dashboard entry operations and guides processing flow seamlessly."""
    user_id = message.from_user.id
    
    # Anti-ban security gate intercept mapping
    conn = get_db_connection()
    u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if u_chk and u_chk['is_banned'] == 1:
        return

    check_and_release_expired_tasks()
    register_user(user_id)
    
    # Global verification status check layer
    if not is_user_joined_all(user_id):
        bot.send_message(
            message.chat.id, 
            "❌ **ACCESS DENIED!**\n\n⚠️ Aapne hamare mandatory channels left kar diye hain.\n🚀 Bot ko wapas use karne ke liye niche diye channels ko join karein!",
            reply_markup=force_join_keyboard()
        )
        return
        
    if message.text == "📨 Get Gmail Task":
        info_header = (
            "🚀 **GMAIL TASK RULES & REWARDS** 🚀\n\n"
            "📌 **Note: Jo Single Mode se Gmail banayega usko ₹15 milega.**\n"
            "🔥 **Lekin agar aap Bulk Mode me 10x Gmail complete karte hain, toh aapko ₹20/Gmail milega!**\n\n"
            "👇 **Niche diye gaye options me se apna task option select karein:**"
        )
        bot.send_message(message.chat.id, info_header, parse_mode="Markdown", reply_markup=task_options_menu())
        
    elif message.text == "💰 Wallet":
        conn = get_db_connection()
        user = conn.execute("SELECT balance, completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        wallet_text = (
            "💳 **AAPKA WALLET PROFILE** 💳\n\n"
            f"💰 **Available Balance:** ₹{user['balance']}\n"
            f"✅ **Total Completed Tasks:** {user['completed_single_tasks']} Gmails\n\n"
            "⚡ *Aapka earning balance 100% safe aur secure hai.*"
        )
        bot.send_message(message.chat.id, wallet_text, parse_mode="Markdown")
        
    elif message.text == "👥 Invite & Earn":
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={user_id}"
        invite_text = (
            "👥 **INVITE & EARN PROGRAM** 👥\n\n"
            "🎁 Apne doston ko bot share karein aur unlimited cash kamayein!\n"
            "💰 **Per Successful Refer:** Aapko instant **₹1** cash reward milega.\n\n"
            f"🔗 **Aapka unique referral link ye raha:**\n`{invite_link}`\n\n"
            "📈 Ise copy karein aur WhatsApp/Telegram par share karein!"
        )
        bot.send_message(message.chat.id, invite_text, parse_mode="Markdown")
        
    elif message.text == "💸 Withdraw":
        conn = get_db_connection()
        user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if user['balance'] >= 15.0:
            msg = bot.send_message(message.chat.id, f"💳 **CURRENT BALANCE:** ₹{user['balance']}\n\n🔢 **Aap kitna amount withdraw karna chahte hain? (Digits me likhein):**")
            bot.register_next_step_handler(msg, ask_upi_id)
        else:
            bot.send_message(message.chat.id, f"❌ **WITHDRAWAL DENIED!**\n\n⚠️ Bot me minimum withdrawal limit **₹15** hai.\n💰 Aapka available balance sirf **₹{user['balance']}** hai. Aur tasks complete karein!")
            
    elif message.text == "📚 Help & Tutorial":
        conn = get_db_connection()
        res = conn.execute("SELECT value FROM settings WHERE key = 'tutorial'").fetchone()
        conn.close()
        content = res['value'] if res else "📹 **No Tutorial Set by Admin yet.**"
        bot.send_message(message.chat.id, content, parse_mode="Markdown")
        
    elif message.text == "☎️ Contact Owner & Help":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📨 Click Here to Chat with Owner", url="https://t.me/Raka_01"))
        bot.send_message(
            message.chat.id, 
            "☎️ **CONTACT SUPPORT CENTRE** ☎️\n\n💬 Agar aapko payment, task ya bot me koi bhi problem aa rahi hai, toh aap direct owner se bat kar sakte hain.\n\n👇 **Direct owner (@Raka_01) se chat karne ke liye niche button par click karein:**", 
            reply_markup=markup, 
            parse_mode="Markdown"
        )

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 10: TRANSACTIONS & WITHDRAWAL LOGIC FLOWS
# ──────────────────────────────────────────────────────────────────────

def ask_upi_id(message):
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        conn = get_db_connection()
        user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if amount < 15.0 or amount > user['balance']:
            bot.send_message(message.chat.id, "❌ **INVALID REQUEST!**\n\n⚠️ Sahi amount dalein. Ya toh aapka input limit (₹15) se kam hai ya wallet balance se zyada.")
            return
        msg = bot.send_message(message.chat.id, "📱 **Ab apni Real UPI ID send karein (E.g. username@upi):**")
        bot.register_next_step_handler(msg, process_withdrawal_admin_review, amount)
    except:
        bot.send_message(message.chat.id, "❌ **FORMAT ERROR!**\n\n⚠️ Amount me sirf numbers/digits hi dalein.")

def process_withdrawal_admin_review(message, amount):
    user_id = message.from_user.id
    upi_id = message.text
    conn = get_db_connection()
    user_data = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user_data or user_data['balance'] < amount:
        bot.send_message(message.chat.id, "❌ **TRANSACTION FAILED!** Low balance detected.")
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
    
    bot.send_message(WITHDRAW_CHANNEL_ID, f"🚨 **NEW WITHDRAWAL PENDING** 🚨\n\n👤 **User ID:** `{user_id}`\n💵 **Amount Deducted:** ₹{amount}\n📱 **UPI ID:** `{upi_id}`\n\nSelect action from panel:", parse_mode="Markdown", reply_markup=wd_markup)

# ──────────────────────────────────────────────────────────────────────
# 🛰 *SECTION 11: ASYNCHRONOUS CALLBACK CONTROLLERS (LOCK & SPAM ENGINE)*
# ──────────────────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    """Processes pipeline callback events cleanly and triggers targeted database states."""
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    # Anti-ban security loop intercept
    conn = get_db_connection()
    u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if u_chk and u_chk['is_banned'] == 1:
        return

    if call.data == "verify_channels":
        if is_user_joined_all(user_id):
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            bot.send_message(chat_id, "🎉 **CONGRATULATIONS!**\n\n✅ Aapke saare channels successfully verify ho gaye hain! Bot functionality unlock ho chuki hai.", reply_markup=main_menu())
            
            u_info = call.from_user
            alert_msg = (
                f"🛰️ **NEW ACTIVE USER DETECTED** 🛰️\n\n"
                f"👤 **Name:** {u_info.first_name} {u_info.last_name if u_info.last_name else ''}\n"
                f"🆔 **User ID:** `{u_info.id}`\n"
                f"📛 **Username:** @{u_info.username if u_info.username else 'N/A'}\n"
                f"───────────────────\n"
                f"📢 *Bande ne hamare mandatory channels successfully join karke bot activate kar liya hai!*"
            )
            try: bot.send_message(ADMIN_ID, alert_msg, parse_mode="Markdown")
            except: pass
        else:
            bot.answer_callback_query(call.id, "❌ Verification failed! Please check channels.", show_alert=True)
        return

    if not is_user_joined_all(user_id) and call.data != "verify_channels":
        bot.answer_callback_query(call.id, "❌ Access Blocked! Pehle channels join verify karein.", show_alert=True)
        return

    if call.data.startswith('wd_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, amount = parts[1], int(parts[2]), float(parts[3])
        conn = get_db_connection()
        if action == "app":
            bot.edit_message_text(f"🟢 **Approved Payout of ₹{amount}**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"✅ **PAYMENT RECEIVED SUCCESSFULLY!**\n\nAapka ₹{amount} ka withdrawal request admin ne approve kar ke paise direct transfer kar diye hain! 🎉")
        elif action == "rej":
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
            conn.commit()
            bot.edit_message_text(f"🔴 **Rejected Payout! Balance Refunded.**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"❌ **WITHDRAWAL REJECTED!**\n\nAapka ₹{amount} ka cash request cancel kar diya gaya hai. Balance aapke wallet me **wapas refund** kar diya gaya hai.")
        conn.close()
        return

    if call.data.startswith('adm_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, session_id, count_override = parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        
        selected_rate = 0.0
        if action == "rate15":
            selected_rate = 15.0
        elif action == "rate20":
            selected_rate = 20.0
            
        conn = get_db_connection()
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        
        if action in ["rate15", "rate20"]:
            if session:
                ids = session['task_id_list'].split(',')
                for t_id in ids:
                    conn.execute("UPDATE task_pool SET status = 'COMPLETED' WHERE id = ?", (int(t_id),))
            
            final_reward = selected_rate * count_override
            conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (final_reward, target_user))
            if count_override == 1:
                conn.execute("UPDATE users SET completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (target_user,))
            conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
            conn.commit()
            
            bot.edit_message_caption(f"🟢 **Approved! Paid ₹{final_reward} ({count_override} Gmails verified at ₹{int(selected_rate)}/ea)**", chat_id, call.message.message_id)
            bot.send_message(target_user, f"🎉 **TASK APPROVED!**\n\nAdmin ne aapka verification proof accept kar liya hai.\n💰 **🔥 ₹{final_reward} Cash Reward** aapke balance me successfully add ho chuka hai!")
            
        elif action == "rej":
            if session:
                ids = session['task_id_list'].split(',')
                for t_id in ids:
                    conn.execute("DELETE FROM task_pool WHERE id = ?", (int(t_id),))
            conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
            conn.commit()
            bot.edit_message_caption("🔴 **Rejected & Destroyed From Stock!**", chat_id, call.message.message_id)
            bot.send_message(target_user, "❌ **Aapka proof reject ho gaya. Credentials stock se permanently delete ho gaye hain.**")
        conn.close()
        return

    conn = get_db_connection()
    if call.data == "task_single":
        task = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 1").fetchone()
        if not task:
            bot.answer_callback_query(call.id, "⚠️ Stock Empty! Admin se bolo aur load karein.", show_alert=True)
            conn.close()
            return
        current_time = int(time.time())
        conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, task['id']))
        cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'SINGLE', ?, ?)", (user_id, str(task['id']), current_time))
        sid = cursor.lastrowid
        conn.commit()
        conn.close()
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Done & Submit Proof", callback_data=f"done_{sid}"),
                   types.InlineKeyboardButton("❌ Cancel Task", callback_data=f"cancel_{sid}"))
        
        task_msg = (
            "📨 **AAPKA SINGLE MODE GMAIL TASK** 📨\n\n"
            f"📧 **Gmail:** `{task['gmail']}`\n"
            f"🔑 **Password:** `{task['password']}`\n\n"
            "⚠️ **Note:** Diye gaye details se successfully account config karke **60 minute** ke andar proof submit karein, warna stock lock release ho jayega!"
        )
        bot.send_message(chat_id, task_msg, parse_mode="Markdown", reply_markup=markup)

    # 📦 HIGH CAPACITY 10x BULK TASK MATRIX CONTROLLER (5x COMPLETION LOCK PROTECTION ENGAGED)
    elif call.data == "task_batch":
        u_data = conn.execute("SELECT completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
        # 🔒 LOCK VERIFICATION LOGIC: Requires exactly 5 completed items to enter bulk space
        if not u_data or u_data['completed_single_tasks'] < 5:
            current_done = u_data['completed_single_tasks'] if u_data else 0
            bot.answer_callback_query(
                call.id, 
                f"🔒 Locked System! Pehle Single mode se kam se kam 5 Gmail complete karo yrr. (Aapka Current Done: {current_done}/5)", 
                show_alert=True
            )
            conn.close()
            return

        tasks = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' LIMIT 10").fetchall()
        if len(tasks) < 10:
            bot.answer_callback_query(call.id, f"😢 Bulk stock low hai! Sirf {len(tasks)} items live hain.", show_alert=True)
            conn.close()
            return
            
        current_time = int(time.time())
        bot.send_message(chat_id, "📦 **10x BULK MODE TASK DASHBOARD** 📦\n\nNiche diye gaye saare accounts line se setup karein. Har Gmail ke niche uska independent submit button diya gaya hai:\n───────────────────")
        
        for index, t in enumerate(tasks, 1):
            conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, t['id']))
            cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'BATCH_ROW', ?, ?)", (user_id, str(t['id']), current_time))
            row_sid = cursor.lastrowid
            
            row_markup = types.InlineKeyboardMarkup(row_width=2)
            row_markup.add(
                types.InlineKeyboardButton("✅ Done (Submit Proof)", callback_data=f"done_{row_sid}"),
                types.InlineKeyboardButton("❌ Cancel Task", callback_data=f"cancel_{row_sid}")
            )
            
            row_text = f"{index}️⃣. 📧 `{t['gmail']}` | 🔑 `{t['password']}`"
            bot.send_message(chat_id, row_text, parse_mode="Markdown", reply_markup=row_markup)
            
        conn.commit()
        conn.close()

    elif call.data.startswith("cancel_"):
        sid = int(call.data.split('_')[1])
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        
        if session:
            ids = session['task_id_list'].split(',')
            for t_id in ids:
                conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(t_id),))
            conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
            
            # 🛡️ ANTI-SPAM AUTO-BAN COUNTER TRACK MATRIX ENGINE
            conn.execute("UPDATE users SET cancel_count = cancel_count + 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            
            # Re-fetch structural values to determine critical status limits
            u_update = conn.execute("SELECT cancel_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
            
            if u_update and u_update['cancel_count'] > 3:
                # Triggers immediate isolated lock status flag
                conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
                conn.commit()
                
                # Despatches real-time security threats data to owner frame
                u_info = call.from_user
                ban_alert_msg = (
                    f"🚨 **SECURITY ALERT: ANTI-SPAM AUTO BAN** 🚨\n\n"
                    f"👤 **User Name:** {u_info.first_name}\n"
                    f"🆔 **User ID:** `{user_id}`\n"
                    f"📛 **Username:** @{u_info.username if u_info.username else 'N/A'}\n"
                    f"⚠️ **Total Cancel Movements:** {u_update['cancel_count']} times\n"
                    f"───────────────────\n"
                    f"🚫 *Bande ne baar-baar stock cancel karke limit cross kar di thi, isliye bot ne use AUTOMATICALLY BAN kar diya hai!*"
                )
                try: bot.send_message(ADMIN_ID, ban_alert_msg, parse_mode="Markdown")
                except: pass
                
                bot.edit_message_text("❌ **Aapka account baar-baar task cancel karne ke karan BAN kar diya gaya hai!**", chat_id, call.message.message_id)
                conn.close()
                return

        bot.edit_message_text("❌ **Task Cancelled!** Item wapas stock pool me load ho gaya hai.", chat_id, call.message.message_id)
        conn.close()

    elif call.data.startswith("done_"):
        sid = int(call.data.split('_')[1])
        msg = bot.send_message(chat_id, "📸 **PROOF SUBMISSION CENTRE**\n\nAapne jo gmail abhi successfully create kiya hai, uska clear image screenshot proof send karein:")
        bot.register_next_step_handler(msg, process_final_channel_proof, sid)
        conn.close()

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 12: EXECUTION THREAD INITIALIZER
# ──────────────────────────────────────────────────────────────────────

print("🚀 Security Auto-Ban engine & 5x Completion validation locks deployed. Online...")
bot.infinity_polling()
