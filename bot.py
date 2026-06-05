import telebot
import sqlite3
import time
import random
import threading  # Multi-threaded concurrent processing pipeline layer for absolute crash isolation
from telebot import types

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 1: SYSTEM IDENTITIES & TELEGRAM GLOBAL PRODUCTION ENVIRONMENT
# ──────────────────────────────────────────────────────────────────────

# Secure master core production token definitions
API_TOKEN = '7990556564:AAFeSZb6lh_Ha-ojnRvEONg4zTAfFu8606c'
ADMIN_ID = 8031127296

# Telegram Routing Endpoint Coordinates Mapping Nodes
GMAIL_CHANNEL_ID = -1003955255909
WITHDRAW_CHANNEL_ID = -1004208044139

# Mandatory Anti-Drain Verification Nodes Channels List Matrix
REQUIRED_CHANNELS = ["@Raka_Works", "@RakaXproof", "@BilibiliWorks"] 

bot = telebot.TeleBot(API_TOKEN)

# System isolation threading lock register instantiation to prevent concurrent memory corruption
db_thread_lock = threading.Lock()

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 2: ARCHITECTURE CORE DATABASE DESIGN (WAL PRODUCTION PROTOCOLS)
# ──────────────────────────────────────────────────────────────────────

def get_db_connection():
    """Returns an isolated relational pointer with extreme production timeouts to bypass database locks."""
    conn = sqlite3.connect('gmail_bot.db', timeout=60.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Bootstraps full schema layout configurations securely if absent from local cluster storage."""
    with db_thread_lock:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Activating extreme production modes for SQLite storage safety
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('PRAGMA synchronous=NORMAL;')
            
            # Master table structure tracking persistent user metadata models
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL DEFAULT 0.0,
                    referred_by INTEGER,
                    completed_single_tasks INTEGER DEFAULT 0,
                    cancel_count INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    refer_reward_paid INTEGER DEFAULT 0
                )
            ''')
            
            # Inventory asset tracking registry model for Single Modes
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
            
            # Review and Rating automation tracker dataset matrix
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS review_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_link TEXT,
                    review_msg TEXT,
                    assigned_to INTEGER DEFAULT NULL,
                    assigned_at INTEGER DEFAULT NULL,
                    status TEXT DEFAULT 'AVAILABLE'
                )
            ''')
            
            # Multi-session dynamic tracker with unified text storage block for unlimited logging
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
            
            # Internal key-value dynamic variables system registry
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Seeding static parameters defaults safely without overwriting old values
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tutorial', '📹 **Help & Tutorial Video:**\n\n[No video link set yet by admin. Use /sethelp to update]')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('review_reward', '5.0')")
            
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lock_single_mode', 'UNLOCK')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lock_unlimited_mode', 'UNLOCK')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lock_history_mode', 'UNLOCK')")
            
            cursor.execute("""INSERT OR IGNORE INTO settings (key, value) VALUES ('unlimited_rule_msg', 'RULE GMAIL NAME ME NHI DUGA KHUD BANANA HAI

1. GMAIL NAME REAL TYPE HONA CHAYEA KISI KA NAME KUCH BHI MAT LIKH DENA

2. GMAIL BANTE TIME AGE 1990 SA 1999 KE BECH MA RAKHNA

3. GMAIL PASSWORD NICHE DIYA HU WO RAKHNA WO SAME HOGA SABMA

4. SUBMIT KE BAAD GMAIL DELETE MAT KARNA PAYMENT ANE KE BAAD GMAIL LOG OUT KARDENA DELETE MAT KARNA

PASSWORD :- `malam222`')""")
            conn.commit()

try:
    init_db()
except Exception as db_init_err:
    print(f"Database Initialization Critical Error Logs: {db_init_err}")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 3: SUBSCRIPTION POLICING & MALICIOUS FILTER ENGINE
# ──────────────────────────────────────────────────────────────────────

def is_user_joined_all(user_id):
    """Enforces absolute real-time structural lookups across target community endpoints."""
    if user_id == ADMIN_ID:
        return True
    
    with db_thread_lock:
        with get_db_connection() as conn:
            u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    
    if u_chk and u_chk['is_banned'] == 1:
        return False
        
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked', 'restricted'] or member.status is None:
                return False
        except Exception:
            return False 
    return True

def force_join_keyboard():
    """Generates direct secure verification inline links for unauthorized connections."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Join @Raka_Works", url=f"https://t.me/{REQUIRED_CHANNELS[0].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @RakaXproof", url=f"https://t.me/{REQUIRED_CHANNELS[1].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @BilibiliWorks", url=f"https://t.me/{REQUIRED_CHANNELS[2].replace('@','')}"),
        types.InlineKeyboardButton("✅ Joined (Verify Account)", callback_data="verify_channels")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 4: ASYNCHRONOUS PIPELINE BACKGROUND WORKERS
# ──────────────────────────────────────────────────────────────────────

def register_user(user_id, referrer_id=None):
    """Binds incoming new registration objects into the atomic structural layout mapping."""
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO users (user_id, referred_by, balance, completed_single_tasks, cancel_count, is_banned, refer_reward_paid) VALUES (?, ?, 0.0, 0, 0, 0, 0)", (user_id, referrer_id,))
                    conn.commit()
    except Exception as reg_err:
        print(f"Error captured in register_user flow: {reg_err}")

def check_and_release_expired_tasks():
    """Releases locked single tasks after 10 minutes timeout rules safely without dropping active rows."""
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                current_time = int(time.time())
                limit_single = current_time - 600 
                
                cursor.execute("SELECT id, user_id, task_type, task_id_list, started_at FROM sessions WHERE status = 'PENDING'")
                all_pending = cursor.fetchall()
                
                for session in all_pending:
                    sid = session['id']
                    uid = session['user_id']
                    t_type = session['task_type']
                    started = session['started_at']
                    
                    if t_type == 'SINGLE' and started < limit_single:
                        if session['task_id_list'] and str(session['task_id_list']).strip():
                            cursor.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE gmail = ?", (str(session['task_id_list']).strip(),))
                        
                        cursor.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                        try:
                            bot.send_message(uid, "⏰ **TIME OUT ALERT!**\n\n⚠️ Aapne **10 minute** ke andar task poora karke submit nahi kiya.\n❌ Isliye aapka task automatically **Cancel** karke system pool se release kar diya gaya hai!")
                        except: pass
                conn.commit()
    except Exception as expiry_err:
        print(f"Error captured in automatic expiry checker execution: {expiry_err}")

def broadcast_stock_worker(added_count, current_total):
    """Executes high-performance transmission alerts without blocking main loop cycles."""
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                user_rows = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        
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
                if count % 25 == 0: time.sleep(1.0)
                else: time.sleep(0.03)
            except Exception: continue
    except Exception as e:
        print(f"Background stock broadcaster runtime loop error log: {e}")

def auto_stock_broadcast_alert(added_count, current_total):
    """Spawns an isolated background worker context to broadcast fresh logs safely."""
    thr = threading.Thread(target=broadcast_stock_worker, args=(added_count, current_total))
    thr.start()

def evaluate_and_release_referral_bonus(target_user_id):
    """Scans and credits affiliate markers instantly when invited members unlock 2 valid check lines."""
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                user_profile = conn.execute("SELECT referred_by, completed_single_tasks, refer_reward_paid FROM users WHERE user_id = ?", (target_user_id,)).fetchone()
                
                if user_profile and user_profile['referred_by'] and user_profile['refer_reward_paid'] == 0:
                    if user_profile['completed_single_tasks'] >= 2:
                        upline_id = user_profile['referred_by']
                        conn.execute("UPDATE users SET balance = balance + 1.0 WHERE user_id = ?", (upline_id,))
                        conn.execute("UPDATE users SET refer_reward_paid = 1 WHERE user_id = ?", (target_user_id,))
                        conn.commit()
                        
                        try:
                            notification_string = (
                                "🎉 **REFERRAL REWARD CREDITED!** 🎉\n\n"
                                f"🤝 Aapke invited member (ID: `{target_user_id}`) ne bot me **2 Gmail Tasks successfully complete** kar liye hain!\n"
                                "💰 **Aapko milta hai: +₹1.00 Cash reward** direct aapke balance profile wallet me! Inviter pipeline logs setup complete! 🚀"
                            )
                            bot.send_message(upline_id, notification_string, parse_mode="Markdown")
                        except: pass
    except Exception as ref_pipeline_err:
        print(f"Failure inside referral transaction calculation handlers: {ref_pipeline_err}")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 5: SCREENSHOT PROOF PROCESSOR & ROUTING ENGINE
# ──────────────────────────────────────────────────────────────────────

def process_final_channel_proof(message, session_id):
    """Tracks submission proofs and hooks high-resolution interactive control nodes into admin panels."""
    if not message.photo:
        bot.send_message(message.chat.id, "❌ **SUBMISSION ERROR!**\n\n⚠️ Proof verification ke liye sirf Photo/Screenshot format hi bhejni hogi. Process reset.")
        return
        
    file_id = message.photo[-1].file_id
    user_id = message.from_user.id
    
    with db_thread_lock:
        with get_db_connection() as conn:
            session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    
    if not session: 
        bot.send_message(message.chat.id, "❌ **SESSION ERROR!** Task record expired or invalid.")
        return
        
    if session['task_type'] == 'UNLIMITED_MODE':
        task_label = "♾️ [UNLIMITED MODE CREATION PROOF]"
        raw_credentials = session['task_id_list']
        gmails_list = [g.strip() for g in raw_credentials.split(',') if g.strip()]
        
        for index, s_gmail in enumerate(gmails_list):
            # CRITICAL ENGINE UPGRADE: Shortened callback data parameters to exactly fit 64-bytes maximum buffer limits
            admin_markup = types.InlineKeyboardMarkup(row_width=1)
            admin_markup.add(
                types.InlineKeyboardButton("🟢 Approve Payout", callback_data=f"unl_app_{session_id}_{index}"),
                types.InlineKeyboardButton("🔴 Reject Creation", callback_data=f"unl_rej_{session_id}_{index}"),
                types.InlineKeyboardButton("🔵 Taken", callback_data=f"unl_tak_{session_id}_{index}")
            )
            
            caption_text = (
                f"🛰️ **NEW PROGRESS UNLIMITED VALIDATION ({index+1}/{len(gmails_list)})** 🛰️\n\n"
                f"📋 **TASK TYPE:** `{task_label}`\n"
                f"👤 **User ID:** `{user_id}`\n\n"
                f"📋 **TARGET EMAIL SPECIFICATION:**\n`{s_gmail}`\n\n"
                f"⚠️ *Select specific response configuration below for this exact email matrix row:* "
            )
            
            if index == 0:
                bot.send_photo(GMAIL_CHANNEL_ID, file_id, caption=caption_text, reply_markup=admin_markup, parse_mode="Markdown")
            else:
                bot.send_message(GMAIL_CHANNEL_ID, text=f"📦 **[EXTENDED BATCH TRACK NODE]**\n\n{caption_text}", reply_markup=admin_markup, parse_mode="Markdown")
                
        bot.send_message(message.chat.id, "⏳ **Proof and accounts data uploaded successfully! Direct item validation blocks generated inside boss audit panel channel. Checking updates logged under your parameters!** 🎉")
        return
        
    elif session['task_type'] == 'REVIEW_TASK':
        review_target_id = int(session['task_id_list'])
        with get_db_connection() as conn:
            review_data = conn.execute("SELECT review_link, review_msg FROM review_pool WHERE id = ?", (review_target_id,)).fetchone()
        target_url = review_data['review_link'] if review_data else "N/A"
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 Approve Review Task", callback_data=f"rev_approve_{user_id}_{session_id}_{review_target_id}"),
            types.InlineKeyboardButton("🔴 Reject Review Task", callback_data=f"rev_reject_{user_id}_{session_id}_{review_target_id}")
        )
        caption_text = f"🛰️ **NEW REVIEW VALIDATION LOG NODE** 🛰️\n\n👤 **User ID:** `{user_id}`\n🔗 **Link:** {target_url}"
        bot.send_photo(GMAIL_CHANNEL_ID, file_id, caption=caption_text, reply_markup=admin_markup, parse_mode="Markdown")
        bot.send_message(message.chat.id, "⏳ Proof uploaded successfully!")
        return

    else:
        task_label = "📨 [SINGLE MODE TASK PROOF]"
        s_gmail_addr = session['task_id_list']
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 Approve Single Task", callback_data=f"sgl_app_{session_id}_0"),
            types.InlineKeyboardButton("🔴 Reject Single Task", callback_data=f"sgl_rej_{session_id}_0"),
            types.InlineKeyboardButton("🔵 Taken", callback_data=f"sgl_tak_{session_id}_0")
        )
        caption_text = f"🛰️ **NEW SINGLE GMAIL VALIDATION** 🛰️\n\n📋 **TASK TYPE:** `{task_label}`\n👤 **User ID:** `{user_id}`\n📧 **Gmail:** `{s_gmail_addr}`\n\nSelect action coefficients from blocks panel:"

    bot.send_photo(GMAIL_CHANNEL_ID, file_id, caption=caption_text, reply_markup=admin_markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "⏳ **Proof uploaded successfully! Aapka screenshot direct audit channel validation panel me bhej diya gaya hai. Next task turant shuru kar sakte hain!** 🎉")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 6: HIGH-FIDELITY INTERACTIVE COMPONENT GRAPHICS
# ──────────────────────────────────────────────────────────────────────

def main_menu():
    """Generates the absolute responsive system interface keyboard layout mapping."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📨 Get Gmail Task")
    btn2 = types.KeyboardButton("💰 Wallet")
    btn3 = types.KeyboardButton("👥 Invite & Earn")
    btn4 = types.KeyboardButton("💸 Withdraw")
    btn5 = types.KeyboardButton("📚 Help & Tutorial")
    btn6 = types.KeyboardButton("⭐ Review Task") 
    
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    markup.add(btn6)
    return markup

def task_options_menu():
    """Constructs inline parameters with clear customized tier pricing models."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📨 1 Gmail Task (₹15)", callback_data="task_single"),
        types.InlineKeyboardButton("♾️ Create Unlimited Gmail (₹15)", callback_data="preview_unlimited"),
        types.InlineKeyboardButton("📋 Your Gmail History", callback_data="history_dashboard_loop")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 7: CORE SIGNALS & INTEGRATION COMMAND PARSERS
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_cmd(message):
    """Processes user entrance vectors and handles cookies dynamically."""
    user_id = message.from_user.id
    
    with db_thread_lock:
        with get_db_connection() as conn:
            u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
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
# 🛰️ SECTION 8: EXTENSIVE ADMINISTRATIVE BACKEND INSTRUMENT SUITE
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['setunlimitedmsg'])
def admin_set_unlimited_mode_rules_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_rules = message.text.replace("/setunlimitedmsg", "").strip()
        if not raw_rules:
            bot.send_message(ADMIN_ID, "❌ **Sahi Format:** `/setunlimitedmsg <write all unlimited mode guidelines here>`")
            return
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('unlimited_rule_msg', ?)", (raw_rules,))
                conn.commit()
        bot.send_message(ADMIN_ID, "✅ **Unlimited Gmail Creation Rule Text updated successfully!**")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Data Injection Error: {e}")

@bot.message_handler(commands=['locksingle'])
def admin_lock_single(message):
    if message.from_user.id != ADMIN_ID: return
    with db_thread_lock:
        with get_db_connection() as conn:
            conn.execute("UPDATE settings SET value = 'LOCK' WHERE key = 'lock_single_mode'")
            conn.commit()
    bot.send_message(ADMIN_ID, "🔒 **Single Gmail Task option has been LOCKED successfully!**")

@bot.message_handler(commands=['unlocksingle'])
def admin_unlock_single(message):
    if message.from_user.id != ADMIN_ID: return
    with db_thread_lock:
        with get_db_connection() as conn:
            conn.execute("UPDATE settings SET value = 'UNLOCK' WHERE key = 'lock_single_mode'")
            conn.commit()
    bot.send_message(ADMIN_ID, "🟢 **Single Gmail Task option has been UNLOCKED successfully!**")

@bot.message_handler(commands=['lockunlimited'])
def admin_lock_unlimited(message):
    if message.from_user.id != ADMIN_ID: return
    with db_thread_lock:
        with get_db_connection() as conn:
            conn.execute("UPDATE settings SET value = 'LOCK' WHERE key = 'lock_unlimited_mode'")
            conn.commit()
    bot.send_message(ADMIN_ID, "🔒 **Create Unlimited Gmail option has been LOCKED successfully!**")

@bot.message_handler(commands=['unlockunlimited'])
def admin_unlock_unlimited(message):
    if message.from_user.id != ADMIN_ID: return
    with db_thread_lock:
        with get_db_connection() as conn:
            conn.execute("UPDATE settings SET value = 'UNLOCK' WHERE key = 'lock_unlimited_mode'")
            conn.commit()
    bot.send_message(ADMIN_ID, "🟢 **Create Unlimited Gmail option has been UNLOCKED successfully!**")

@bot.message_handler(commands=['ban'])
def admin_manual_ban(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            bot.send_message(ADMIN_ID, "❌ **Format:** `/ban USER_ID`")
            return
        target_uid = int(parts[1])
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (target_uid,))
                conn.commit()
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
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("UPDATE users SET is_banned = 0, cancel_count = 0 WHERE user_id = ?", (target_uid,))
                conn.commit()
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
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0.0)", (target_uid,))
                conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_uid))
                conn.commit()
                new_bal = conn.execute("SELECT balance FROM users WHERE user_id = ?", (target_uid,)).fetchone()['balance']
        bot.send_message(ADMIN_ID, f"✅ **Balance Added Successfully!**\n👤 User: `{target_uid}`\n💰 New Balance: ₹{new_bal}")
        try: bot.send_message(target_uid, f"🎁 **BONUS RECEIVED!**\n\nAdmin ne aapke wallet me **Extra ₹{amount}** credit kiye hain! 🎉\n💰 **Current Balance:** ₹{new_bal}")
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
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
                conn.commit()
                count = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        
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
        with db_thread_lock:
            with get_db_connection() as conn:
                for line in lines:
                    if ":" in line:
                        try:
                            gmail, password = line.strip().split(":", 1)
                            conn.execute("INSERT INTO task_pool (gmail, password, status) VALUES (?, ?, 'AVAILABLE')", (gmail.strip(), password.strip()))
                            success_count += 1
                        except: pass
                conn.commit()
                total_stock = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        
        bot.send_message(ADMIN_ID, f"📦 **Bulk Import Status:**\n✅ Added: {success_count}\n🔥 Total Live Stock: {total_stock}\n📢 *All users background threads executed smoothly!*")
        if success_count > 0:
            auto_stock_broadcast_alert(success_count, total_stock)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Bulk Add Error:** {e}")

@bot.message_handler(commands=['viewtask'])
def admin_view_stock_fixed(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                stock_tasks = conn.execute("SELECT id, gmail, password FROM task_pool WHERE status = 'AVAILABLE' ORDER BY id ASC LIMIT 30").fetchall()
                total_available = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        
        if not stock_tasks:
            bot.send_message(ADMIN_ID, "📦 **Stock Empty Hai!** Database pool me koi bhi live task nahi mila.")
            return
            
        stock_text = f"🔥 **LIVE AVAILABLE STOCK LIST (Total: {total_available})** 🔥\n\n"
        for task in stock_tasks:
            stock_text += f"🆔 `ID: {task['id']}`\n📧 `{task['gmail']}`\n🔑 `{task['password']}`\n───────────────────\n"
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
        with db_thread_lock:
            with get_db_connection() as conn:
                task_check = conn.execute("SELECT * FROM task_pool WHERE id = ? AND status = 'AVAILABLE'", (task_id,)).fetchone()
                if not task_check:
                    bot.send_message(ADMIN_ID, f"❌ **Task ID `{task_id}` Live Stock me nahi mili.**")
                    return
                conn.execute("DELETE FROM task_pool WHERE id = ?", (task_id,))
                conn.commit()
        bot.send_message(ADMIN_ID, f"🗑️ **Stock Se Deleted!**\n🆔 Task ID: `{task_id}` has been dropped from live pool forever.")
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
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("UPDATE task_pool SET gmail = ?, password = ? WHERE id = ?", (new_gmail.strip(), new_password.strip(), task_id))
                conn.commit()
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
        with db_thread_lock:
            with get_db_connection() as conn:
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('tutorial', ?)", (new_content,))
                conn.commit()
        bot.send_message(ADMIN_ID, "✅ **Help & Tutorial message updated in database successfully!**")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ **Set Help Error:** {e}")

@bot.message_handler(commands=['broadcast'])
def admin_broadcast_flexible(message):
    if message.from_user.id != ADMIN_ID: return
    text_to_send = message.text.replace("/broadcast", "").strip()
    if not text_to_send:
        bot.send_message(ADMIN_ID, "❌ **Format:** `/broadcast Write any global message here`")
        return
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                users = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        
        count = 0
        failed_count = 0
        status_msg = bot.send_message(ADMIN_ID, f"📢 **Broadcast Shuru Ho Gaya Hai...**\nTotal Users in DB: {len(users)}")
        
        for u in users:
            try:
                bot.send_message(chat_id=u['user_id'], text=text_to_send, disable_web_page_preview=False)
                count += 1
                if count % 20 == 0: time.sleep(1.0)
                else: time.sleep(0.05)
            except telebot.apihelper.ApiTelegramException: failed_count += 1; continue
            except Exception: failed_count += 1; continue
                
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
        with db_thread_lock:
            with get_db_connection() as conn:
                user = conn.execute("SELECT * FROM users WHERE user_id = ?", (target_uid,)).fetchone()
        if user:
            bot.send_message(ADMIN_ID, f"🔍 **User Info:**\n👤 ID: `{target_uid}`\n💰 Balance: ₹{user['balance']}\n✅ Completed: {user['completed_single_tasks']}\n⚠️ Cancel Rows: {user['cancel_count']}\n🚫 Ban Status: {user['is_banned']}")
    except Exception as e: pass

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 9: INTERACTIVE GRAPHICAL CORE CONTROLLER LOGIC
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_text_messages(message):
    """Processes pipeline events securely and maps texts to core targets."""
    user_id = message.from_user.id
    
    with db_thread_lock:
        with get_db_connection() as conn:
            u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if u_chk and u_chk['is_banned'] == 1:
        return

    check_and_release_expired_tasks()
    register_user(user_id)
    
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
            "📌 **Rule: Create Gmail And Select 1990-1999 If You Select 2000 your gmail Rejected And After Paid Payment Logout Gmail In Your phone Don''t Delete Gmail Only Logout**\n\n"
            "───────────────────\n"
            "📌 **Note: Jo Single Mode se Gmail banayega usko ₹15 milega (10 Min Expiry).**\n"
            "🔥 **Lekin agar aap Bulk Mode me 10x Gmail complete karte hain, toh aapko ₹20/Gmail milega (60 Min Expiry)!**\n\n"
            "👇 **Niche diye gaye options me se apna task option select karein:**"
        )
        bot.send_message(message.chat.id, info_header, parse_mode="Markdown", reply_markup=task_options_menu())
        
    elif message.text == "💰 Wallet":
        with db_thread_lock:
            with get_db_connection() as conn:
                user = conn.execute("SELECT balance, completed_single_tasks FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
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
            "💰 **Per Successful Refer:** Aapko instant **₹1** cash reward tab milega jab jisko refer kiya hai wo banda kam se kam **2 Gmail Tasks complete** karega! 🤝\n\n"
            f"🔗 **Aapka unique referral link ye raha:**\n`{invite_link}`\n\n"
            "📈 Ise copy karein aur WhatsApp/Telegram par share karein!"
        )
        bot.send_message(message.chat.id, invite_text, parse_mode="Markdown")
        
    elif message.text == "💸 Withdraw":
        with db_thread_lock:
            with get_db_connection() as conn:
                user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
        if user['balance'] >= 15.0:
            msg = bot.send_message(message.chat.id, f"💳 **CURRENT BALANCE:** ₹{user['balance']}\n\n🔢 **Aap kitna amount withdraw karna chahte hain? (Digits me likhein):**")
            bot.register_next_step_handler(msg, ask_upi_id)
        else:
            bot.send_message(message.chat.id, f"❌ **WITHDRAWAL DENIED!**\n\n⚠️ Bot me minimum withdrawal limit **₹15** hai.\n💰 Aapka available balance sirf **₹{user['balance']}** hai. Aur tasks complete karein!")
            
    elif message.text == "📚 Help & Tutorial":
        with db_thread_lock:
            with get_db_connection() as conn:
                res = conn.execute("SELECT value FROM settings WHERE key = 'tutorial'").fetchone()
        content = res['value'] if res else "📹 **No Tutorial Set by Admin yet.**"
        bot.send_message(message.chat.id, content, parse_mode="Markdown")
        
    elif message.text == "⭐ Review Task":
        with db_thread_lock:
            with get_db_connection() as conn:
                review = conn.execute("SELECT * FROM review_pool WHERE status = 'AVAILABLE' ORDER BY id ASC LIMIT 1").fetchone()
        
        if not review:
            bot.send_message(message.chat.id, "⚠️ **No Review Task Available!**\n\n⚡ Pool me filhal koi review task stock nahi hai. Admin jaise hi naye tasks load karenge, aapko notify kar diya jayega yrr!")
            return
            
        current_time = int(time.time())
        with db_thread_lock:
            with get_db_connection() as conn:
                r_reward = conn.execute("SELECT value FROM settings WHERE key = 'review_reward'").fetchone()['value']
                conn.execute("UPDATE review_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, review['id']))
                cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'REVIEW_TASK', ?, ?)", (user_id, str(review['id']), current_time))
                sid = cursor.lastrowid
                conn.commit()
        
        review_dashboard_text = (
            "⭐ **DYNAMIC RATING & REVIEW TASK** ⭐\n\n"
            f"💰 **Task Reward Earning:** `₹{r_reward} Cash Balance` (Direct Wallet)\n"
            "───────────────────\n"
            f"🔗 **Review Link Map Path:**\n{review['review_link']}\n\n"
            f"📝 **Review Text Requirements (Copy it):**\n`{review['review_msg']}`\n"
            "───────────────────\n"
            "⚠️ **Instructions:** Upar diye gaye link par jaakar text paste karke dynamic review karein, aur uske baad niche diye button se apna screenshot proof file submit karein yrr!"
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✅ Done (Submit Proof)", callback_data=f"done_{sid}"),
            types.InlineKeyboardButton("❌ Cancel Task", callback_data=f"cancel_{sid}")
        )
        bot.send_message(message.chat.id, review_dashboard_text, parse_mode="Markdown", reply_markup=markup)

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 10: CASH REWARD WITHDRAWAL REVIEW FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def ask_upi_id(message):
    try:
        amount = float(message.text)
        user_id = message.from_user.id
        with db_thread_lock:
            with get_db_connection() as conn:
                user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
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
    
    with db_thread_lock:
        with get_db_connection() as conn:
            user_data = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if not user_data or user_data['balance'] < amount:
                bot.send_message(message.chat.id, "❌ **TRANSACTION FAILED!** Low balance detected.")
                return
                
            conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
            conn.commit()
    
    wd_markup = types.InlineKeyboardMarkup()
    wd_markup.add(
        types.InlineKeyboardButton("🟢 Approve Payout", callback_data=f"wd_app_{user_id}_{amount}"),
        types.InlineKeyboardButton("🔴 Reject Payout", callback_data=f"wd_rej_{user_id}_{amount}")
    )
    success_text = f"✅ **\"Withdrawal Request Submitted!\"**\n\n💰 **\"Amount:\"** ₹{amount}\n📱 **\"UPI ID:\"** {upi_id}\n\n⚠️ **\"Payment Under 24 Hours\"**"
    bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
    bot.send_message(WITHDRAW_CHANNEL_ID, f"🚨 **NEW WITHDRAWAL PENDING** 🚨\n\n👤 **User ID:** `{user_id}`\n💵 **Amount Deducted:** ₹{amount}\n📱 **UPI ID:** `{upi_id}`\n\nSelect action from panel:", parse_mode="Markdown", reply_markup=wd_markup)

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 11: DISPATCH ASYNCHRONOUS ENGINE (CALLBACK ROUTERS)
# ──────────────────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    """Monitors callback execution paths across distributed system scopes securely."""
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    with db_thread_lock:
        with get_db_connection() as conn:
            u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if u_chk and u_chk['is_banned'] == 1:
        return

    if call.data == "verify_channels":
        if is_user_joined_all(user_id):
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            bot.send_message(chat_id, "🎉 **CONGRATULATIONS!**\n\n✅ Aapke saare channels successfully verify ho gaye hain! Bot functionality unlock ho chuki hai.", reply_markup=main_menu())
        else:
            bot.answer_callback_query(call.id, "❌ Verification failed! Please check channels.", show_alert=True)
        return

    if not is_user_joined_all(user_id) and call.data != "verify_channels":
        bot.answer_callback_query(call.id, "❌ Access Blocked! Pehle channels join verify karein.", show_alert=True)
        return

    # HISTORICAL GRAPH DASHBOARD LOGGER
    if call.data == "history_dashboard_loop":
        with db_thread_lock:
            with get_db_connection() as conn:
                history_rows = conn.execute("SELECT task_id_list, status FROM sessions WHERE user_id = ? AND task_type IN ('SINGLE', 'UNLIMITED_MODE') ORDER BY id DESC LIMIT 25").fetchall()
        
        if not history_rows:
            bot.send_message(chat_id, "📋 **YOUR GMAIL SUBMISSION HISTORY** 📋\n\n⚠️ Aapne abhi tak bot me koi bhi Gmail account submit nahi kiya hai yrr!")
            return
            
        history_text = "📋 **YOUR GMAIL SUBMISSION HISTORY** 📋\n\n"
        for index, row in enumerate(history_rows, 1):
            raw_target_emails = row['task_id_list']
            display_status = "Pending"
            if row['status'] == 'APPROVED': display_status = "Success"
            elif row['status'] == 'REJECTED': display_status = "Invalid"
            elif row['status'] == 'TAKEN': display_status = "Success"
            
            history_text += f"{index}️⃣. 📧 `{raw_target_emails}`\n📊 **Status:** `{display_status}`\n───────────────────\n"
            
        bot.send_message(chat_id, history_text, parse_mode="Markdown")
        return

    # FIXED SHORTENED UNLIMITED MODE DISPATCH DECODER PROTOCOL
    if call.data.startswith("unl_"):
        if call.from_user.id != ADMIN_ID: return
        parts = call.data.split("_")
        action_type, session_id, target_index = parts[1], int(parts[2]), int(parts[3])
        
        with db_thread_lock:
            with get_db_connection() as conn:
                session_data = conn.execute("SELECT user_id, task_id_list FROM sessions WHERE id = ?", (session_id,)).fetchone()
                
        if not session_data:
            bot.answer_callback_query(call.id, "❌ Session parameters not found inside persistent stack register!", show_alert=True)
            return
            
        target_user = session_data['user_id']
        emails_parsed = [e.strip() for e in session_data['task_id_list'].split(',') if e.strip()]
        
        if target_index >= len(emails_parsed):
            bot.answer_callback_query(call.id, "❌ Index tracking misalignment error inside memory array grids!", show_alert=True)
            return
            
        s_gmail = emails_parsed[target_index]
        
        if action_type == "app":
            with db_thread_lock:
                with get_db_connection() as conn:
                    conn.execute("UPDATE users SET balance = balance + 15.0 WHERE user_id = ?", (target_user,))
                    conn.execute("UPDATE users SET completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (target_user,))
                    conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
                    conn.commit()
            try: bot.edit_message_caption(f"🟢 **Approved email: {s_gmail}! Paid ₹15 value increments.**", chat_id, call.message.message_id)
            except: bot.edit_message_text(f"🟢 **Approved email: {s_gmail}! Paid ₹15 value increments.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, f"🎉 **UNLIMITED GMAIL APPROVED!**\n\n📧 **Gmail ID:** `{s_gmail}`\n💰 Aapka ye account accept ho gaya hai aur iska point balance credit kar diya gaya hai! 💸")
            except: pass
            evaluate_and_release_referral_bonus(target_user)
            
        elif action_type == "rej":
            with db_thread_lock:
                with get_db_connection() as conn:
                    conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
                    conn.commit()
            try: bot.edit_message_caption(f"🔴 **Rejected email: {s_gmail}! Notification sent to user.**", chat_id, call.message.message_id)
            except: bot.edit_message_text(f"🔴 **Rejected email: {s_gmail}! Notification sent to user.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, f"❌ **Apka Gmail Reject ho gaya hai!**\n\n📧 **Gmail ID:** `{s_gmail}`\n⚠️ Payout credit nahi kiya gaya hai, kripya sahi rules follow karein!")
            except: pass
            
        elif action_type == "tak":
            with db_thread_lock:
                with get_db_connection() as conn:
                    conn.execute("UPDATE sessions SET status = 'TAKEN' WHERE id = ?", (session_id,))
                    conn.commit()
            try: bot.edit_message_caption(f"🔵 **Taken email: {s_gmail}! Notice sent to user.**", chat_id, call.message.message_id)
            except: bot.edit_message_text(f"🔵 **Taken email: {s_gmail}! Notice sent to user.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, f"💼 **STATUS UPDATE: ACCOUNT TAKEN**\n\n📧 **Gmail ID:** `{s_gmail}`\n\nAapka gmail Successfully boss ko submit kardiya gaya hai. Aab Aap Checking ka Wait Kare yrr! ⏳")
            except: pass
        return

    # FIXED SHORTENED SINGLE MODE DISPATCH DECODER PROTOCOL
    if call.data.startswith("sgl_"):
        if call.from_user.id != ADMIN_ID: return
        parts = call.data.split("_")
        action_type, session_id = parts[1], int(parts[2])
        
        with db_thread_lock:
            with get_db_connection() as conn:
                session_data = conn.execute("SELECT user_id, task_id_list FROM sessions WHERE id = ?", (session_id,)).fetchone()
                
        if not session_data:
            bot.answer_callback_query(call.id, "❌ Session record not found inside arrays stack space!", show_alert=True)
            return
            
        target_user = session_data['user_id']
        s_gmail = session_data['task_id_list']
        
        if action_type == "app":
            with db_thread_lock:
                with get_db_connection() as conn:
                    conn.execute("UPDATE users SET balance = balance + 15.0 WHERE user_id = ?", (target_user,))
                    conn.execute("UPDATE users SET completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (target_user,))
                    conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
                    conn.commit()
            bot.edit_message_caption(f"🟢 **Single Task Approved email: {s_gmail}! Paid ₹15.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, f"🎉 **SINGLE MODE GMAIL APPROVED!**\n\n📧 **Gmail ID:** `{s_gmail}`\n💰 Aapka task verification accept ho gaya hai! Reward credited! 💸")
            except: pass
            evaluate_and_release_referral_bonus(target_user)
            
        elif action_type == "rej":
            with db_thread_lock:
                with get_db_connection() as conn:
                    conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
                    conn.commit()
            bot.edit_message_caption(f"🔴 **Single Task Rejected email: {s_gmail}! Warning alerts issued.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, f"❌ **Apka Gmail Reject ho gaya hai!**\n\n📧 **Gmail ID:** `{s_gmail}`\n⚠️ Layout checklist rules check karein, iska points balance add nahi hua.")
            except: pass
            
        elif action_type == "tak":
            with db_thread_lock:
                with get_db_connection() as conn:
                    conn.execute("UPDATE sessions SET status = 'TAKEN' WHERE id = ?", (session_id,))
                    conn.commit()
            bot.edit_message_caption(f"🔵 **Single Task Taken email: {s_gmail}! Pending checks notice sent.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, f"💼 **STATUS UPDATE: ACCOUNT TAKEN**\n\n📧 **Gmail ID:** `{s_gmail}`\n\nAapka gmail Successfully boss ko submit kardiya gaya hai. Aab Aap Checking ka Wait Kare yrr! ⏳")
            except: pass
        return

    if call.data.startswith("rev_"):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, session_id, review_pool_id = parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        
        with db_thread_lock:
            with get_db_connection() as conn:
                if action == "approve":
                    r_reward = float(conn.execute("SELECT value FROM settings WHERE key = 'review_reward'").fetchone()['value'])
                    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (r_reward, target_user))
                    conn.execute("UPDATE review_pool SET status = 'COMPLETED' WHERE id = ?", (review_pool_id,))
                    conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
                    conn.commit()
                    bot.edit_message_caption(f"🟢 **Review Task Approved! Paid ₹{r_reward} to User direct wallet balance.**", chat_id, call.message.message_id)
                elif action == "reject":
                    conn.execute("UPDATE review_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (review_pool_id,))
                    conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
                    conn.commit()
                    bot.edit_message_caption("🔴 **Review Task Rejected! Status reset to AVAILABLE inside isolated registers.**", chat_id, call.message.message_id)
        return

    if call.data.startswith('wd_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, amount = parts[1], int(parts[2]), float(parts[3])
        with db_thread_lock:
            with get_db_connection() as conn:
                if action == "app":
                    bot.edit_message_text(f"🟢 **Approved Payout of ₹{amount}**", chat_id, call.message.message_id)
                    bot.send_message(target_user, f"✅ **PAYMENT RECEIVED SUCCESSFULLY!**\n\nAapka ₹{amount} ka withdrawal request admin ne approve kar ke paise direct transfer kar diye hain! 🎉")
                elif action == "rej":
                    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
                    conn.commit()
                    bot.edit_message_text(f"🔴 **Rejected Payout! Balance Refunded.**", chat_id, call.message.message_id)
                    bot.send_message(target_user, f"❌ **WITHDRAWAL REJECTED!**\n\nAapka ₹{amount} ka cash request cancel kar diya gaya hai. Balance aapke wallet me **wapas refund** kar diya gaya hai.")
        return

    if call.data == "task_single":
        with db_thread_lock:
            with get_db_connection() as conn:
                lock_chk = conn.execute("SELECT value FROM settings WHERE key = 'lock_single_mode'").fetchone()['value']
                if lock_chk == 'LOCK':
                    bot.answer_callback_query(call.id, "🔒 Locked! Admin ne Single Gmail Task option ko filhal temporary closed kiya hai yrr!", show_alert=True)
                    return

                task = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' ORDER BY random() LIMIT 1").fetchone()
                if not task:
                    bot.answer_callback_query(call.id, "⚠️ Stock Empty! Admin se bolo aur load karein.", show_alert=True)
                    return
                current_time = int(time.time())
                conn.execute("UPDATE task_pool SET status = 'LOCKED', assigned_to = ?, assigned_at = ? WHERE id = ?", (user_id, current_time, task['id']))
                cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'SINGLE', ?, ?)", (user_id, str(task['gmail']), current_time))
                sid = cursor.lastrowid
                conn.commit()
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Done & Submit Proof", callback_data=f"done_{sid}"),
                   types.InlineKeyboardButton("❌ Cancel Task", callback_data=f"cancel_{sid}"))
        
        task_msg = (
            "📨 **AAPKA SINGLE MODE GMAIL TASK** 📨\n\n"
            f"📧 **Gmail:** `{task['gmail']}`\n"
            f"🔑 **Password:** `{task['password']}`\n\n"
            "⚠️ **Note:** Diye gaye details se successfully account config karke **10 minute** ke andar proof submit karein, warna stock lock release ho jayega!"
        )
        bot.send_message(chat_id, task_msg, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "preview_unlimited":
        with db_thread_lock:
            with get_db_connection() as conn:
                lock_chk = conn.execute("SELECT value FROM settings WHERE key = 'lock_unlimited_mode'").fetchone()['value']
                if lock_chk == 'LOCK':
                    bot.answer_callback_query(call.id, "🔒 Locked! Admin ne Create Unlimited Gmail option ko filhal temporary closed kiya hai yrr!", show_alert=True)
                    return
                rules_msg = conn.execute("SELECT value FROM settings WHERE key = 'unlimited_rule_msg'").fetchone()['value']
            
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("✅ Sahi Hai (Submit Gmail + SS)", callback_data="task_unlimited"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_preview_mode")
        )
        
        bot.send_message(
            chat_id, 
            f"📋 **CREATE UNLIMITED GMAIL: STRATIFIED RULES** 📋\n\n{rules_msg}\n\n⚠️ **Important:** Upar diye gaye saare rules ko dhyan se padhein, uske baad hi niche button par click karke details submit karein!", 
            parse_mode="Markdown", 
            reply_markup=markup
        )

    elif call.data == "task_unlimited":
        try: bot.delete_message(chat_id, call.message.message_id)
        except: pass
        
        unlimited_input_prompt = (
            "♾️ **CREATE UNLIMITED GMAIL CENTRE** ♾️\n\n"
            "Aapne jo fresh unique accounts create kiye hain unki list neeche diye gaye format me type karke send karein yrr!\n\n"
            "🔥 **Advanced Update:** Agar ek se zyada Gmail bhej rahe hain, toh unhe comma (,) laga kar ek sath bhej sakte hain!\n\n"
            "👉 **Format:** `Email1, Email2, Email3` (Aapko sirf pehle email ka screenshot proof manga jayega, baaki bina proof ke direct submit ho jayenge!)\n\n"
            "📝 **Example:**\n`RakeshManu716@Gmail.com, RakeshKumar88@Gmail.com`"
        )
        msg = bot.send_message(chat_id, unlimited_input_prompt, parse_mode="Markdown")
        bot.register_next_step_handler(msg, check_unlimited_batch_inputs_count)

    elif call.data == "cancel_preview_mode":
        try: bot.delete_message(chat_id, call.message.message_id)
        except: pass
        bot.send_message(chat_id, "❌ **Task Cancelled!** Creation pipeline reset to safe configuration limits.", reply_markup=main_menu())

    elif call.data.startswith("cancel_"):
        sid = int(call.data.split('_')[1])
        with get_db_connection() as conn:
            session = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
            if session:
                if session['task_type'] == 'SINGLE':
                    with get_db_connection() as conn_release:
                        conn_release.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE gmail = ?", (session['task_id_list'],))
                        conn_release.commit()
                
                conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                if session['task_type'] not in ['REVIEW_TASK', 'UNLIMITED_MODE']:
                    conn.execute("UPDATE users SET cancel_count = cancel_count + 1 WHERE user_id = ?", (user_id,))
                    conn.commit()
                    u_update = conn.execute("SELECT cancel_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
                    
                    if u_update and u_update['cancel_count'] > 3:
                        conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
                        conn.commit()
                        try: bot.edit_message_text("❌ **Aapka account baar-baar task cancel karne ke karan BAN kar diya gaya hai!**", chat_id, call.message.message_id)
                        except: pass
                        return
                else:
                    conn.commit()

        bot.edit_message_text("❌ **Task Cancelled successfully and state released safely out of layers!**", chat_id, call.message.message_id)

    elif call.data.startswith("done_"):
        sid = int(call.data.split('_')[1])
        msg = bot.send_message(chat_id, "📸 **PROOF SUBMISSION CENTRE**\n\nAapne jo task abhi successfully kiya hai, uska clear image screenshot proof send karein:")
        bot.register_next_step_handler(msg, process_final_channel_proof, sid)

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 11.5: STEP HANDLERS ENGINE FOR UNLIMITED BATCH SELECTION
# ──────────────────────────────────────────────────────────────────────

def check_unlimited_batch_inputs_count(message):
    """Processes mass text variables data configurations securely into database layout streams."""
    user_id = message.from_user.id
    raw_input_text = message.text
    
    if not raw_input_text:
        bot.send_message(message.chat.id, "❌ **INPUT ERROR!** Process reset. Dubara try karein.")
        return
        
    evaluated_gmails = [g.strip() for g in raw_input_text.split(',') if g.strip()]
    
    if not evaluated_gmails:
        bot.send_message(message.chat.id, "❌ Sahi entries nahi mili. Try again.")
        return
        
    current_time = int(time.time())
    
    if len(evaluated_gmails) > 1:
        with db_thread_lock:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'UNLIMITED_MODE', ?, ?)", (user_id, raw_input_text.strip(), current_time))
                sid = cursor.lastrowid
                conn.commit()
                
        for index, b_gmail in enumerate(evaluated_gmails):
            # FIXED BY USING INDEX STRINGS MATRIX LOOKUPS FOR CRASH FREE CHANNELS CAPACITIES 
            admin_markup = types.InlineKeyboardMarkup(row_width=1)
            admin_markup.add(
                types.InlineKeyboardButton("🟢 Approve Payout", callback_data=f"unl_app_{sid}_{index}"),
                types.InlineKeyboardButton("🔴 Reject Creation", callback_data=f"unl_rej_{sid}_{index}"),
                types.InlineKeyboardButton("🔵 Taken", callback_data=f"unl_tak_{sid}_{index}")
            )
            
            caption_text = (
                f"🛰️ **NEW MULTI-BATCH UNLIMITED SUBMISSION ({index+1}/{len(evaluated_gmails)})** 🛰️\n\n"
                f"📋 **TASK TYPE:** `♾️ [UNLIMITED BATCH ENGINE]`\n"
                f"👤 **User ID:** `{user_id}`\n\n"
                f"📋 **TARGET EMAIL SPECIFICATION:**\n`{b_gmail}`\n\n"
                f"⚡ *[NO SCREENSHOT PROOF REQUIRED FOR EXTENDED MULTI-BATCH ITEMS]*"
            )
            bot.send_message(GMAIL_CHANNEL_ID, text=caption_text, reply_markup=admin_markup, parse_mode="Markdown")
            
        bot.send_message(message.chat.id, "⚡ **Multi-Batch Accounts detected successfully!** Aapki saari entries bina screenshot proof mange direct boss checking panel me successfully register aur forward kar di gayi hain yrr! Check history dashboard to follow updates. 🚀")
        
    else:
        with db_thread_lock:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'UNLIMITED_MODE', ?, ?)", (user_id, raw_input_text.strip(), current_time))
                sid = cursor.lastrowid
                conn.commit()
                
        msg = bot.send_message(message.chat.id, "📸 **Ab is create kiye huye account ka clear image screenshot proof bhejyein:**")
        bot.register_next_step_handler(msg, process_final_channel_proof, sid)

def capture_unlimited_text_credentials(message):
    pass

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 12: RELIABLE INFINITY POLLING PRODUCTION SUITE
# ──────────────────────────────────────────────────────────────────────

print("🚀 PRODUCTION MASTER ENGINE ONLINE: All button character length limits fixed and locked. Polling live...")
bot.infinity_polling()
