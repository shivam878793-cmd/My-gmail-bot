import telebot
import sqlite3
import time
import random
import threading  # Multi-threaded concurrent processing pipeline layer
from telebot import types

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 1: SYSTEM IDENTITIES & TELEGRAM GLOBAL VARIABLES
# ──────────────────────────────────────────────────────────────────────

# Secure master core production string definitions 
API_TOKEN = '7990556564:AAFeSZb6lh_Ha-ojnRvEONg4zTAfFu8606c'
ADMIN_ID = 8031127296

# Telegram Routing Endpoint Coordinates Mapping
GMAIL_CHANNEL_ID = -1003955255909
WITHDRAW_CHANNEL_ID = -1004208044139

# Mandatory Anti-Drain Verification Nodes Channels List
REQUIRED_CHANNELS = ["@Raka_Works", "@RakaXproof", "@BilibiliWorks"] 

bot = telebot.TeleBot(API_TOKEN)

# System isolation threading lock register instantiation to prevent data state racing and drop-outs
db_thread_lock = threading.Lock()

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 2: ARCHITECTURE CORE DATABASE DESIGN (WAL MODE & TIMEOUTS)
# ──────────────────────────────────────────────────────────────────────

def get_db_connection():
    """Returns an isolated relational pointer with extreme timeouts to bypass database locked bugs."""
    conn = sqlite3.connect('gmail_bot.db', timeout=60.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Bootstraps database structural schema layers if absent from runtime local execution space."""
    with db_thread_lock:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('PRAGMA synchronous=NORMAL;')
            
            # Master structure execution blocks mapping user metadata configurations
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
            
            # Review Task Storage System Schema Layout Model
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
            
            # UPGRADED SESSIONS SCHEMA: Mapped data rows layout fields securely to track multiple infinite creation pools logs
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
            
            # Seed static parameters defaults if records do not exist
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tutorial', '📹 **Help & Tutorial Video:**\\n\\n[No video link set yet by admin. Use /sethelp to update]')")
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
# 🛰️ SECTION 3: SYSTEM WALLS & BANNED LOCK MECHANISMS
# ──────────────────────────────────────────────────────────────────────

def is_user_joined_all(user_id):
    """Enforces rigorous structural lookups across external channel states before responding."""
    if user_id == ADMIN_ID:
        return True
    
    # Security Intercept Layer Check via strict atomic thread encapsulation
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
    """Generates immediate target coordinate links for non-compliant subscriber logs."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Join @Raka_Works", url=f"https://t.me/{REQUIRED_CHANNELS[0].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @RakaXproof", url=f"https://t.me/{REQUIRED_CHANNELS[1].replace('@','')}"),
        types.InlineKeyboardButton("📢 Join @BilibiliWorks", url=f"https://t.me/{REQUIRED_CHANNELS[2].replace('@','')}"),
        types.InlineKeyboardButton("✅ Joined (Verify Account)", callback_data="verify_channels")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 4: PIPELINE WORKERS & BACKGROUND EXPIRE PROTOCOLS
# ──────────────────────────────────────────────────────────────────────

def register_user(user_id, referrer_id=None):
    """Saves non-existing dynamic elements to database system instantly during initial handshakes."""
    try:
        with db_thread_lock:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO users (user_id, referred_by, balance, completed_single_tasks, cancel_count, is_banned, refer_reward_paid) VALUES (?, ?, 0.0, 0, 0, 0, 0)", (user_id, referrer_id,))
                    conn.commit()
    except Exception as reg_err:
        print(f"Error captured in register_user flow execution maps: {reg_err}")

def check_and_release_expired_tasks():
    """Releases locked stock based on single task 10 minutes timeout rules without dynamic balance purges."""
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
                    
                    if t_type == 'SINGLE':
                        if started < limit_single:
                            if session['task_id_list'] and session['task_id_list'].isdigit():
                                cursor.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(session['task_id_list']),))
                            
                            cursor.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                            try:
                                bot.send_message(uid, "⏰ **TIME OUT ALERT!**\n\n⚠️ Aapne **10 minute** ke andar task poora karke submit nahi kiya.\n❌ Isliye aapka task automatically **Cancel** karke system pool se release kar diya gaya hai!")
                            except: pass
                conn.commit()
    except Exception as expiry_err:
        print(f"Error captured in automatic expiry checker execution: {expiry_err}")

def broadcast_stock_worker(added_count, current_total):
    """Processes mass notification loops inside a separate standalone thread context safely."""
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
        print(f"Background thread runtime loop failure log: {e}")

def auto_stock_broadcast_alert(added_count, current_total):
    """Dispatches asynchronous alerts across background execution matrices."""
    thr = threading.Thread(target=broadcast_stock_worker, args=(added_count, current_total))
    thr.start()

def evaluate_and_release_referral_bonus(target_user_id):
    """Scans historical confirmation indices to credit upline structures automatically upon two successful tasks validation checks."""
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
        print(f"Failure inside referral transaction calculation handlers loops: {ref_pipeline_err}")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 5: ADVANCED PHOTO PROOF SCREENSHOT PARSING PIPELINE
# ──────────────────────────────────────────────────────────────────────

def process_final_channel_proof(message, session_id):
    """Processes verification screenshots and attaches live trace links to the admin audit panel."""
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
            admin_markup = types.InlineKeyboardMarkup(row_width=1)
            admin_markup.add(
                types.InlineKeyboardButton("🟢 Approve Payout", callback_data=f"unl_approve_{user_id}_{session_id}_{s_gmail}"),
                types.InlineKeyboardButton("🔴 Reject Creation", callback_data=f"unl_reject_{user_id}_{session_id}_{s_gmail}"),
                types.InlineKeyboardButton("🔵 Taken", callback_data=f"unl_taken_{user_id}_{session_id}_{s_gmail}")
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
            types.InlineKeyboardButton("🟢 Approve Single Task", callback_data=f"sgl_approve_{user_id}_{session_id}_{s_gmail_addr}"),
            types.InlineKeyboardButton("🔴 Reject Single Task", callback_data=f"sgl_reject_{user_id}_{session_id}_{s_gmail_addr}"),
            types.InlineKeyboardButton("🔵 Taken", callback_data=f"sgl_taken_{user_id}_{session_id}_{s_gmail_addr}")
        )
        caption_text = f"🛰️ **NEW SINGLE GMAIL VALIDATION** 🛰️\n\n📋 **TASK TYPE:** `{task_label}`\n👤 **User ID:** `{user_id}`\n📧 **Gmail:** `{s_gmail_addr}`\n\nSelect action coefficients from blocks panel:"

    bot.send_photo(GMAIL_CHANNEL_ID, file_id, caption=caption_text, reply_markup=admin_markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "⏳ **Proof uploaded successfully! Aapka screenshot direct audit channel validation panel me bhej diya gaya hai. Next task turant shuru kar sakte hain!** 🎉")

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 6: HIGH-FIDELITY USER EXPERIENCE INTERACTION GRAPHICS
# ──────────────────────────────────────────────────────────────────────

def main_menu():
    """Generates the absolute responsive interface menu parameters mapped directly into standard devices."""
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
    """Constructs the primary branching inline parameters with customized pricing format mappings."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📨 1 Gmail Task (₹15)", callback_data="task_single"),
        types.InlineKeyboardButton("♾️ Create Unlimited Gmail (₹15)", callback_data="preview_unlimited"),
        types.InlineKeyboardButton("📋 Your Gmail History", callback_data="history_dashboard_loop")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 7: CORE REGISTRATION GATEWAYS & COMMAND PARSERS
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_cmd(message):
    """Processes initial entrance steps and binds unique affiliate cookies dynamically."""
    user_id = message.from_user.id
    
    with db_thread_lock:
        with get_db_connection() as conn:
            u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
    if u_chk and u_chk['is_banned'] == 1:
        bot.send_message(message.chat.id, "❌ **Aapka account admin dwara permanently block/ban kar diya gaya hai.**")
        return
        
    text = me
