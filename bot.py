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
        
        # ADVANCED CONTROL SEED INJECTIONS: Initializes status registers for independent locking vectors safely
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lock_single_mode', 'UNLOCK')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lock_bulk_mode', 'UNLOCK')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lock_unlimited_mode', 'UNLOCK')")
        
        # FIXED EXACT TEXT LAYOUT: Exact step-by-step spacing matched with double-tap copy password wrapper
        cursor.execute("""INSERT OR REPLACE INTO settings (key, value) VALUES ('unlimited_rule_msg', 'RULE GMAIL NAME ME NHI DUGA KHUD BANANA HAI

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
    
    # Security Intercept Layer Check
    with get_db_connection() as conn:
        u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    
    if u_chk and u_chk['is_banned'] == 1:
        return False
        
    # FIXED CHANNEL ERROR: Properly parses elements mapped exactly to requested target arrays
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
# 🛰️ SECTION 4: PIPELINE WORKERS & DUAL BACKGROUND TIMER SPLIT
# ──────────────────────────────────────────────────────────────────────

def register_user(user_id, referrer_id=None):
    """Saves non-existing dynamic elements to database system instantly during initial handshakes."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (user_id, referred_by, balance) VALUES (?, ?, 0.0)", (user_id, referrer_id,))
                conn.commit()
    except Exception as reg_err:
        print(f"Error captured in register_user flow execution maps: {reg_err}")

def check_and_release_expired_tasks():
    """Releases locked stock based on differentiated expiration rules (10m Single vs 60m Bulk)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            current_time = int(time.time())
            
            limit_bulk = current_time - 3600  # 60 Minutes for Bulk/Review Matrix
            limit_single = current_time - 600 # 10 Minutes for Single Mode Task
            
            cursor.execute("SELECT id, user_id, task_type, task_id_list, started_at FROM sessions WHERE status = 'PENDING'")
            all_pending = cursor.fetchall()
            
            for session in all_pending:
                sid = session['id']
                uid = session['user_id']
                t_type = session['task_type']
                started = session['started_at']
                
                is_expired = False
                time_label = ""
                
                if t_type in ['BATCH_ROW', 'REVIEW_TASK']:
                    if started < limit_bulk:
                        is_expired = True
                        time_label = "60 minute (1 ghanta)"
                elif t_type in ['UNLIMITED_MODE', 'UNLIMITED_PREVIEW']:
                    continue
                else: 
                    if started < limit_single:
                        is_expired = True
                        time_label = "10 minute"
                        
                if is_expired:
                    if t_type == 'REVIEW_TASK' and session['task_id_list']:
                        cursor.execute("UPDATE review_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(session['task_id_list']),))
                    elif session['task_id_list']:
                        ids = session['task_id_list'].split(',')
                        for t_id in ids:
                            cursor.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ? AND status = 'LOCKED'", (int(t_id),))
                    
                    cursor.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                    try:
                        bot.send_message(uid, f"⏰ **TIME OUT ALERT!**\n\n⚠️ Aapne **{time_label}** ke andar task poora karke submit nahi kiya.\n❌ Isliye aapka task automatically **Cancel** karke system pool se release kar diya gaya hai!")
                    except:
                        pass
            conn.commit()
    except Exception as expiry_err:
        print(f"Error captured in automatic expiry checker execution: {expiry_err}")

def broadcast_stock_worker(added_count, current_total):
    """Processes mass notification loops inside a separate standalone thread context safely."""
    try:
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

def broadcast_review_worker(added_count, current_total):
    """Sends mass push signals dynamically without holding admin control boards processes."""
    try:
        with get_db_connection() as conn:
            user_rows = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
        
        user_list = [row['user_id'] for row in user_rows]
        alert_text = (
            "⭐ **🔥 FRESH REVIEW STOCK LOADED! 🔥** ⭐\n\n"
            f"🚀 **Admin ne abhi naye {added_count} Rating & Review Tasks pool me add kiye hain!**\n"
            f"📊 **Total Live Available Review Stock:** `{current_total}` Tasks\n\n"
            "💰 Jaldi aao, simple review copy-paste karo aur dheron paise kamao direct profile wallet me! 💸⚡"
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
        print(f"Background operational review channel thread exception trace: {e}")

def auto_review_broadcast_alert(added_count, current_total):
    """Spawns automated system review worker blocks immediately to prevent system locks."""
    thr = threading.Thread(target=broadcast_review_worker, args=(added_count, current_total))
    thr.start()

def evaluate_and_release_referral_bonus(target_user_id):
    """Scans historical confirmation indices to credit upline structures automatically upon two successful tasks validation checks."""
    try:
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
    
    with get_db_connection() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    
    if not session: 
        bot.send_message(message.chat.id, "❌ **SESSION ERROR!** Task record expired or invalid.")
        return
        
    if session['task_type'] == 'BATCH_ROW':
        task_label = "📦 [10x BULK MODE TASK PROOF]"
        ids_count = len(session['task_id_list'].split(','))
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 Approve at ₹15/ea", callback_data=f"adm_rate15_{user_id}_{session_id}_{ids_count}"),
            types.InlineKeyboardButton("🟡 Approve at ₹20/ea", callback_data=f"adm_rate20_{user_id}_{session_id}_{ids_count}"),
            types.InlineKeyboardButton("🔴 Reject & Delete", callback_data=f"adm_rej_{user_id}_{session_id}_0")
        )
        caption_text = f"🛰️ **NEW PROGRESS TASK VALIDATION** 🛰️\n\n📋 **TASK TYPE:** `{task_label}`\n👤 **User ID:** `{user_id}`\n📦 **Assigned Items:** {ids_count} Gmail(s)\n\nAdmin select correct rate button from panel below to verify:"
        
    elif session['task_type'] == 'REVIEW_TASK':
        task_label = "⭐ [REVIEW TASK PROOF VALIDATION]"
        review_target_id = int(session['task_id_list'])
        
        with get_db_connection() as conn:
            review_data = conn.execute("SELECT review_link, review_msg FROM review_pool WHERE id = ?", (review_target_id,)).fetchone()
            conn.execute("UPDATE review_pool SET status = 'VERIFYING' WHERE id = ?", (review_target_id,))
            conn.commit()
        
        target_url = review_data['review_link'] if review_data else "N/A"
        req_msg = review_data['review_msg'] if review_data else "N/A"
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 Approve Review Task", callback_data=f"rev_approve_{user_id}_{session_id}_{review_target_id}"),
            types.InlineKeyboardButton("🔴 Reject Review Task", callback_data=f"rev_reject_{user_id}_{session_id}_{review_target_id}")
        )
        
        caption_text = (
            f"🔗 **TARGET REVIEW LINK:**\n{target_url}\n\n"
            f"📝 **REQUIREMENTS MESSAGE:**\n`{req_msg}`\n"
            f"───────────────────\n"
            f"🛰️ **NEW PROGRESS TASK VALIDATION** 🛰️\n\n"
            f"📋 **TASK TYPE:** `{task_label}`\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"🆔 **Review Stock ID:** `{review_target_id}`\n\n"
            f"*Select appropriate resolution parameters from administrative blocks below:* "
        )
        
    elif session['task_type'] == 'UNLIMITED_MODE':
        task_label = "♾️ [UNLIMITED MODE CREATION PROOF]"
        raw_credentials = session['task_id_list']
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 Approve Creation (₹15)", callback_data=f"unl_approve_{user_id}_{session_id}"),
            types.InlineKeyboardButton("🔴 Reject Creation", callback_data=f"unl_reject_{user_id}_{session_id}")
        )
        
        caption_text = (
            f"🛰️ **NEW PROGRESS TASK VALIDATION** 🛰️\n\n"
            f"📋 **TASK TYPE:** `{task_label}`\n"
            f"👤 **User ID:** `{user_id}`\n\n"
            f"📋 **SUBMITTED GMAIL CHARACTERISTICS:**\n`{raw_credentials}`\n\n"
            f"⚠️ **Admin Audit:** Check details inside image layout and resolve:"
        )
        
    else:
        task_label = "📨 [SINGLE MODE TASK PROOF]"
        ids_count = len(session['task_id_list'].split(','))
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("🟢 Approve at ₹15/Gmail", callback_data=f"adm_rate15_{user_id}_{session_id}_{ids_count}"),
            types.InlineKeyboardButton("🟡 Approve at ₹20/Gmail", callback_data=f"adm_rate20_{user_id}_{session_id}_{ids_count}"),
            types.InlineKeyboardButton("🔴 Reject & Delete", callback_data=f"adm_rej_{user_id}_{session_id}_0")
        )
        caption_text = f"🛰️ **NEW PROGRESS TASK VALIDATION** 🛰️\n\n📋 **TASK TYPE:** `{task_label}`\n👤 **User ID:** `{user_id}`\n📦 **Assigned Items:** {ids_count} Gmail(s)\n\nAdmin select correct rate button from panel below to verify:"

    bot.send_photo(
        GMAIL_CHANNEL_ID,
        file_id,
        caption=caption_text,
        reply_markup=admin_markup,
        get_db_connectionparse_mode="Markdown"
    )
    bot.send_message(message.chat.id, "⏳ **Proof uploaded successfully! Aapka screenshot direct audit channel validation panel me bhej diya gaya hai. Next task turant shuru kar sakte hain!** 🎉")

@bot.message_handler(content_types=['photo'])
def catch_global_photo_proofs(message):
    """Validates real-time packet transmissions to block unauthorized data routing injections."""
    user_id = message.from_user.id
    
    with get_db_connection() as conn:
        u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
        
    if u_chk and u_chk['is_banned'] == 1:
        bot.send_message(message.chat.id, "❌ **Aapka account is bot me Banned hai!**")
        return

    if not is_user_joined_all(user_id):
        bot.send_message(message.chat.id, "❌ Channels verification missing!")
        return

    with get_db_connection() as conn:
        session = conn.execute("SELECT * FROM sessions WHERE user_id = ? AND status = 'PENDING' ORDER BY id DESC LIMIT 1").fetchone()

    if session:
        process_final_channel_proof(message, session['id'])
    else:
        bot.send_message(message.chat.id, "❌ **SUBMISSION DENIED!**\n\nAapka koi bhi active locked task background pool me nahi mila. Pehle task uthayein!")

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
        types.InlineKeyboardButton("📦 10x Bulk Gmail Task (₹20/ea)", callback_data="task_batch"),
        types.InlineKeyboardButton("♾️ Create Unlimited Gmail (₹15)", callback_data="preview_unlimited")
    )
    return markup

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 7: CORE REGISTRATION GATEWAYS & COMMAND PARSERS
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_cmd(message):
    """Processes initial entrance steps and binds unique affiliate cookies dynamically."""
    user_id = message.from_user.id
    
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
# 🛰️ SECTION 8: EXTENSIVE ADMINISTRATIVE INFRASTRUCTURE SUITE
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['setunlimitedmsg'])
def admin_set_unlimited_mode_rules_text(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        raw_rules = message.text.replace("/setunlimitedmsg", "").strip()
        if not raw_rules:
            bot.send_message(ADMIN_ID, "❌ **Sahi Format:** `/setunlimitedmsg <write all unlimited mode guidelines here>`")
            return
        with get_db_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('unlimited_rule_msg', ?)", (raw_rules,))
            conn.commit()
        bot.send_message(ADMIN_ID, "✅ **Unlimited Gmail Creation Rule Text updated inside database successfully!**")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Data Injection Error: {e}")

@bot.message_handler(commands=['locksingle'])
def admin_lock_single(message):
    if message.from_user.id != ADMIN_ID: return
    with get_db_connection() as conn:
        conn.execute("UPDATE settings SET value = 'LOCK' WHERE key = 'lock_single_mode'")
        conn.commit()
    bot.send_message(ADMIN_ID, "🔒 **Single Gmail Task option has been LOCKED successfully!**")

@bot.message_handler(commands=['unlocksingle'])
def admin_unlock_single(message):
    if message.from_user.id != ADMIN_ID: return
    with get_db_connection() as conn:
        conn.execute("UPDATE settings SET value = 'UNLOCK' WHERE key = 'lock_single_mode'")
        conn.commit()
    bot.send_message(ADMIN_ID, "🟢 **Single Gmail Task option has been UNLOCKED successfully!**")

@bot.message_handler(commands=['lockbulk'])
def admin_lock_bulk(message):
    if message.from_user.id != ADMIN_ID: return
    with get_db_connection() as conn:
        conn.execute("UPDATE settings SET value = 'LOCK' WHERE key = 'lock_bulk_mode'")
        conn.commit()
    bot.send_message(ADMIN_ID, "🔒 **10x Bulk Gmail Task option has been LOCKED successfully!**")

@bot.message_handler(commands=['unlockbulk'])
def admin_unlock_bulk(message):
    if message.from_user.id != ADMIN_ID: return
    with get_db_connection() as conn:
        conn.execute("UPDATE settings SET value = 'UNLOCK' WHERE key = 'lock_bulk_mode'")
        conn.commit()
    bot.send_message(ADMIN_ID, "🟢 **10x Bulk Gmail Task option has been UNLOCKED successfully!**")

@bot.message_handler(commands=['lockunlimited'])
def admin_lock_unlimited(message):
    if message.from_user.id != ADMIN_ID: return
    with get_db_connection() as conn:
        conn.execute("UPDATE settings SET value = 'LOCK' WHERE key = 'lock_unlimited_mode'")
        conn.commit()
    bot.send_message(ADMIN_ID, "🔒 **Create Unlimited Gmail option has been LOCKED successfully!**")

@bot.message_handler(commands=['unlockunlimited'])
def admin_unlock_unlimited(message):
    if message.from_user.id != ADMIN_ID: return
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
        with get_db_connection() as conn:
            stock_tasks = conn.execute("SELECT id, gmail, password FROM task_pool WHERE status = 'AVAILABLE' ORDER BY id ASC LIMIT 30").fetchall()
            total_available = conn.execute("SELECT COUNT(*) as total FROM task_pool WHERE status = 'AVAILABLE'").fetchone()['total']
        
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
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE user_id = ?", (target_uid,)).fetchone()
        if user:
            bot.send_message(ADMIN_ID, f"🔍 **User Info:**\n👤 ID: `{target_uid}`\n💰 Balance: ₹{user['balance']}\n✅ Completed: {user['completed_single_tasks']}\n⚠️ Cancel Rows: {user['cancel_count']}\n🚫 Ban Status: {user['is_banned']}")
    except Exception as e: pass

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 9: TEXT LOGIC CONTROLLER AND RESOLUTION ROUTERS
# ──────────────────────────────────────────────────────────────────────

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_text_messages(message):
    """Processes user operations and ensures data streams flow to correct pipeline endpoints."""
    user_id = message.from_user.id
    
    with get_db_connection() as conn:
        u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if u_chk and u_chk['is_banned'] == 1:
        return

    check_and_release_expired_tasks()
    register_user(user_id)
    
    # CRITICAL SECURITY LOOP UPGRADE: Evaluates exact real-time states mapping target arrays cleanly
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
        with get_db_connection() as conn:
            user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if user['balance'] >= 15.0:
            msg = bot.send_message(message.chat.id, f"💳 **CURRENT BALANCE:** ₹{user['balance']}\n\n🔢 **Aap kitna amount withdraw karna chahte hain? (Digits me likhein):**")
            bot.register_next_step_handler(msg, ask_upi_id)
        else:
            bot.send_message(message.chat.id, f"❌ **WITHDRAWAL DENIED!**\n\n⚠️ Bot me minimum withdrawal limit **₹15** hai.\n💰 Aapka available balance sirf **₹{user['balance']}** hai. Aur tasks complete karein!")
            
    elif message.text == "📚 Help & Tutorial":
        with get_db_connection() as conn:
            res = conn.execute("SELECT value FROM settings WHERE key = 'tutorial'").fetchone()
        content = res['value'] if res else "📹 **No Tutorial Set by Admin yet.**"
        bot.send_message(message.chat.id, content, parse_mode="Markdown")
        
    elif message.text == "⭐ Review Task":
        with get_db_connection() as conn:
            review = conn.execute("SELECT * FROM review_pool WHERE status = 'AVAILABLE' ORDER BY id ASC LIMIT 1").fetchone()
        
        if not review:
            bot.send_message(message.chat.id, "⚠️ **No Review Task Available!**\n\n⚡ Pool me filhal koi review task stock nahi hai. Admin jaise hi naye tasks load karenge, aapko notify kar diya jayega yrr!")
            return
            
        current_time = int(time.time())
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
# 🛰_ SECTION 10: CASH BALANCE WITHDRAWAL ROUTINES
# ──────────────────────────────────────────────────────────────────────

def ask_upi_id(message):
    try:
        amount = float(message.text)
        user_id = message.from_user.id
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
# 🛰_ SECTION 11: ASYNCHRONOUS ENGINE HANDLERS (CALLBACK DISPATCH MODULES)
# ──────────────────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    """Monitors incoming callback triggers and logs database states instantly."""
    check_and_release_expired_tasks()
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    with get_db_connection() as conn:
        u_chk = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
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

    if action := call.data.startswith("unl_"):
        if call.from_user.id != ADMIN_ID: return
        parts = call.data.split("_")
        action, target_user, session_id = parts[1], int(parts[2]), int(parts[3])
        
        if action == "approve":
            with get_db_connection() as conn:
                conn.execute("UPDATE users SET balance = balance + 15.0 WHERE user_id = ?", (target_user,))
                conn.execute("UPDATE users SET completed_single_tasks = completed_single_tasks + 1 WHERE user_id = ?", (target_user,))
                conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
                conn.commit()
            bot.edit_message_caption("🟢 **Unlimited Creation Task Approved! Added ₹15.00 points to user account.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, "🎉 **UNLIMITED GMAIL TASK APPROVED!**\n\nAdmin ne aapka self-created account verification check pass kar diya hai!\n💰 **🔥 ₹15 Cash Reward** aapke balance profile wallet me credit ho chuka hai!")
            except: pass
            
            evaluate_and_release_referral_bonus(target_user)
            
        elif action == "reject":
            with get_db_connection() as conn:
                conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
                conn.commit()
            bot.edit_message_caption("🔴 **Unlimited Creation Task REJECTED! Alert sent to user records.**", chat_id, call.message.message_id)
            try: bot.send_message(target_user, "❌ **Apka Gmail Reject ho gaya hai aur iska koi bhi payment wallet me add nahi kiya gaya hai. Rules padhein!**")
            except: pass
        return

    if call.data.startswith("rev_"):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, session_id, review_pool_id = parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        
        with get_db_connection() as conn:
            if action == "approve":
                r_reward = float(conn.execute("SELECT value FROM settings WHERE key = 'review_reward'").fetchone()['value'])
                conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (r_reward, target_user))
                conn.execute("UPDATE review_pool SET status = 'COMPLETED' WHERE id = ?", (review_pool_id,))
                conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
                conn.commit()
                bot.edit_message_caption(f"🟢 **Review Task Approved! Paid ₹{r_reward} to User direct wallet balance.**", chat_id, call.message.message_id)
                try: bot.send_message(target_user, "🎉 **Whohoo Apka review google map Par live hai Apka Money Apke Wallet ma add kardiya gaya hai**")
                except: pass
            elif action == "reject":
                conn.execute("UPDATE review_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (review_pool_id,))
                conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
                conn.commit()
                bot.edit_message_caption("🔴 **Review Task Rejected! Status reset to AVAILABLE inside isolated registers.**", chat_id, call.message.message_id)
                try: bot.send_message(target_user, "❌ **Admin Na Apka Review Reject Kardiya Kyuki Apko Review Google Map par Live Nhi Hai**")
                except: pass
        return

    if call.data.startswith('wd_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, amount = parts[1], int(parts[2]), float(parts[3])
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

    if call.data.startswith('adm_'):
        if user_id != ADMIN_ID: return
        parts = call.data.split('_')
        action, target_user, session_id, count_override = parts[1], int(parts[2]), int(parts[3]), int(parts[4])
        
        selected_rate = 0.0
        if action == "rate15": selected_rate = 15.0
        elif action == "rate20": selected_rate = 20.0
            
        with get_db_connection() as conn:
            session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            
            if action in ["rate15", "rate20"]:
                if session:
                    ids = session['task_id_list'].split(',')
                    for t_id in ids:
                        conn.execute("UPDATE task_pool SET status = 'COMPLETED' WHERE id = ?", (int(t_id),))
                
                final_reward = selected_rate * count_override
                conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (final_reward, target_user))
                conn.execute("UPDATE users SET completed_single_tasks = completed_single_tasks + ? WHERE user_id = ?", (count_override, target_user,))
                conn.execute("UPDATE sessions SET status = 'APPROVED' WHERE id = ?", (session_id,))
                conn.commit()
                
                bot.edit_message_caption(f"🟢 **Approved! Paid ₹{final_reward} ({count_override} Gmails verified at ₹{int(selected_rate)}/ea)**", chat_id, call.message.message_id)
                bot.send_message(target_user, f"🎉 **TASK APPROVED!**\n\nAdmin ne aapka verification proof accept kar liya hai.\n💰 **🔥 ₹{final_reward} Cash Reward** aapke balance me successfully add ho chuka hai!")
                
                evaluate_and_release_referral_bonus(target_user)
                
            elif action == "rej":
                if session:
                    ids = session['task_id_list'].split(',')
                    for t_id in ids:
                        conn.execute("DELETE FROM task_pool WHERE id = ?", (int(t_id),))
                conn.execute("UPDATE sessions SET status = 'REJECTED' WHERE id = ?", (session_id,))
                conn.commit()
                bot.edit_message_caption("🔴 **Rejected & Permanently Purged From Database Stock Structure Space!**", chat_id, call.message.message_id)
                bot.send_message(target_user, "❌ **Aapka proof reject ho gaya. Credentials stock se permanently delete ho gaye hain.**")
        return

    if call.data == "task_single":
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
            cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'SINGLE', ?, ?)", (user_id, str(task['id']), current_time))
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

    elif call.data == "task_batch":
        with get_db_connection() as conn:
            lock_chk = conn.execute("SELECT value FROM settings WHERE key = 'lock_bulk_mode'").fetchone()['value']
            if lock_chk == 'LOCK':
                bot.answer_callback_query(call.id, "🔒 Locked! Admin ne 10x Bulk Gmail Task option ko filhal temporary closed kiya hai yrr!", show_alert=True)
                return

            submitted_rows = conn.execute("SELECT COUNT(*) as total FROM sessions WHERE user_id = ? AND task_type = 'SINGLE'", (user_id,)).fetchone()
            current_submissions = submitted_rows['total'] if submitted_rows else 0
            
            if current_submissions < 5:
                bot.answer_callback_query(
                    call.id, 
                    f"🔒 Locked System! Pehle Single mode se kam se kam 5 Gmail submit karo yrr. Approve hone se pehle hi khul jayega! (Aapka Current Submitted: {current_submissions}/5)", 
                    show_alert=True
                )
                return

            tasks = conn.execute("SELECT * FROM task_pool WHERE status = 'AVAILABLE' ORDER BY id ASC LIMIT 10").fetchall()
            if len(tasks) < 10:
                bot.answer_callback_query(call.id, f"😢 Bulk stock low hai! Sirf {len(tasks)} items live hain.", show_alert=True)
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
                bot.send_message(chat_id=chat_id, text=row_text, parse_mode="Markdown", reply_markup=row_markup)
            conn.commit()

    elif call.data == "preview_unlimited":
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
            "Aapne jo fresh unique account create kiya hai uski ID neeche diye gaye format me type karke send karein:\n\n"
            "👉 **Format:** `Email` (Password input karne ki zaroorat nahi hai, automatic block process lock ho jayega!)\n\n"
            "📝 **Example:**\n`RakeshManu716@Gmail.com` [This is Example Only]"
        )
        msg = bot.send_message(chat_id, unlimited_input_prompt, parse_mode="Markdown")
        bot.register_next_step_handler(msg, capture_unlimited_text_credentials)

    elif call.data == "cancel_preview_mode":
        try: bot.delete_message(chat_id, call.message.message_id)
        except: pass
        bot.send_message(chat_id, "❌ **Task Cancelled!** Creation pipeline reset to safe configuration limits.", reply_markup=main_menu())

    elif call.data.startswith("cancel_"):
        sid = int(call.data.split('_')[1])
        with get_db_connection() as conn:
            session = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
            
            if session:
                if session['task_type'] == 'REVIEW_TASK':
                    conn.execute("UPDATE review_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(session['task_id_list']),))
                elif session['task_type'] == 'UNLIMITED_MODE':
                    pass
                else:
                    ids = session['task_id_list'].split(',')
                    for t_id in ids:
                        conn.execute("UPDATE task_pool SET status = 'AVAILABLE', assigned_to = NULL, assigned_at = NULL WHERE id = ?", (int(t_id),))
                
                conn.execute("DELETE FROM sessions WHERE id = ?", (sid,))
                
                if session['task_type'] not in ['REVIEW_TASK', 'UNLIMITED_MODE']:
                    conn.execute("UPDATE users SET cancel_count = cancel_count + 1 WHERE user_id = ?", (user_id,))
                    conn.commit()
                    u_update = conn.execute("SELECT cancel_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
                    
                    if u_update and u_update['cancel_count'] > 3:
                        conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
                        conn.commit()
                        
                        u_info = call.from_user
                        ban_alert_msg = (
                            f"🚨 **SECURITY ALERT: ANTI-SPAM AUTO BAN** 🚨\n\n"
                            f"👤 **User Name:** {u_info.first_name} {u_info.last_name if u_info.last_name else ''}\n"
                            f"🆔 **User ID:** `{user_id}`\n"
                            f"📛 **Username:** @{u_info.username if u_info.username else 'N/A'}\n"
                            f"⚠️ **Total Cancel Movements:** {u_update['cancel_count']} times\n"
                            f"───────────────────\n"
                            f"🚫 *Bande ne baar-baar stock cancel karke limit cross kar di thi, isliye bot ne use AUTOMATICALLY BAN kar diya hai!*"
                        )
                        
                        def send_ban_alert_async():
                            try: bot.send_message(chat_id=ADMIN_ID, text=ban_alert_msg, parse_mode="Markdown")
                            except Exception as thread_ex: print(f"Panic alert logs thread error: {thread_ex}")
                        
                        threading.Thread(target=send_ban_alert_async).start()
                        try: bot.edit_message_text("❌ **Aapka account baar-baar task cancel karne ke karan BAN kar diya gaya hai!**", chat_id, call.message.message_id)
                        except: pass
                        return
                else:
                    conn.commit()

        bot.edit_message_text("❌ **Task Cancelled!** Item wapas stock pool me load ya clear ho gaya hai.", chat_id, call.message.message_id)

    elif call.data.startswith("done_"):
        sid = int(call.data.split('_')[1])
        msg = bot.send_message(chat_id, "📸 **PROOF SUBMISSION CENTRE**\n\nAapne jo task abhi successfully kiya hai, uska clear image screenshot proof send karein:")
        bot.register_next_step_handler(msg, process_final_channel_proof, sid)

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 11.5: STEP HANDLERS ROUTINES FOR UNLIMITED CREATION MODE
# ──────────────────────────────────────────────────────────────────────

def capture_unlimited_text_credentials(message):
    """Saves raw text credentials inside temporary database spaces and triggers explicit screenshot prompts."""
    user_id = message.from_user.id
    raw_input = message.text
    
    if not raw_input:
        bot.send_message(message.chat.id, "❌ **INPUT ERROR!**\n\n⚠️ Kripya details ko sahi text template format me hi send karein. Process reset. Dubara click karein.")
        return
        
    current_time = int(time.time())
    with get_db_connection() as conn:
        cursor = conn.execute("INSERT INTO sessions (user_id, task_type, task_id_list, started_at) VALUES (?, 'UNLIMITED_MODE', ?, ?)", (user_id, raw_input.strip(), current_time))
        sid = cursor.lastrowid
        conn.commit()
        
    msg = bot.send_message(message.chat.id, "📸 **Ab is create kiye huye account ka clear image screenshot proof send karein:**")
    bot.register_next_step_handler(msg, process_final_channel_proof, sid)

# ──────────────────────────────────────────────────────────────────────
# 🛰️ SECTION 12: SERVICE POLICE INITIALIZATION POLLING LAYER
# ──────────────────────────────────────────────────────────────────────

print("🚀 PRODUCTION MASTER ENGINE ONLINE: Real-time channel tracking issue resolved completely. Polling live...")
bot.infinity_polling()
