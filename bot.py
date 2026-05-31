import telebot
import sqlite3
import time
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '7990556564:AAFYUQrYcQ7UmwbmFdjPShBFk_kLVYepRpA'
ADMIN_ID = 8031127296
PROOF_CHANNEL_ID = -1003955255909
WITHDRAWAL_CHANNEL_ID = -1004208044139

bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect('gmail_bot.db', check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0, completed_single_tasks INTEGER DEFAULT 0)')
    db.execute('CREATE TABLE IF NOT EXISTS task_pool (id INTEGER PRIMARY KEY AUTOINCREMENT, gmail TEXT, password TEXT, status TEXT DEFAULT "AVAILABLE")')
    db.execute('CREATE TABLE IF NOT EXISTS sessions (user_id INTEGER PRIMARY KEY, task_type TEXT, task_id_list TEXT, started_at INTEGER)')
    db.commit()
    db.close()

init_db()

# --- COMMANDS & LOGIC ---
@bot.message_handler(commands=['start'])
def start(m):
    db = get_db()
    db.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (m.chat.id,))
    db.commit()
    db.close()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📨 Get Gmail Task", "💰 Wallet", "👥 Invite & Earn", "💸 Withdraw", "📚 Help & Tutorial")
    bot.send_message(m.chat.id, "👋 **Welcome! Gmail Task Bot me aapka swagat hai.**\n\n👇 Task complete karein aur paise kamayein!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📨 Get Gmail Task")
def task_menu(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📨 1 Gmail Task", callback_data="single"),
               types.InlineKeyboardButton("📦 0/10 Gmail Task", callback_data="batch"))
    bot.send_message(m.chat.id, "🗂️ **Select Task Mode:**", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 Wallet")
def wallet(m):
    db = get_db()
    u = db.execute('SELECT balance, completed_single_tasks FROM users WHERE user_id = ?', (m.chat.id,)).fetchone()
    bot.send_message(m.chat.id, f"💳 **Wallet Details:**\n💰 Balance: ₹{u['balance']}\n✅ Completed: {u['completed_single_tasks']}")
    db.close()

# --- WITHDRAWAL SYSTEM ---
@bot.message_handler(func=lambda m: m.text == "💸 Withdraw")
def withdraw_start(m):
    db = get_db()
    bal = db.execute('SELECT balance FROM users WHERE user_id = ?', (m.chat.id,)).fetchone()['balance']
    db.close()
    if bal < 15:
        bot.send_message(m.chat.id, f"❌ **Min withdrawal ₹15 hai.** Current balance: ₹{bal}")
    else:
        msg = bot.send_message(m.chat.id, "🔢 **Kitna amount withdraw karna hai?**")
        bot.register_next_step_handler(msg, lambda m2: ask_upi(m2, m2.text))

def ask_upi(m, amt):
    try:
        if float(amt) < 15: raise Exception
        msg = bot.send_message(m.chat.id, "📱 **Ab apni Real UPI ID bhejein:**")
        bot.register_next_step_handler(msg, lambda m2: finish_withdraw(m2, amt, m2.text))
    except: bot.send_message(m.chat.id, "❌ Valid amount dalein (Min ₹15).")

def finish_withdraw(m, amt, upi):
    db = get_db()
    db.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amt, m.chat.id))
    db.commit()
    db.close()
    bot.send_message(m.chat.id, "✅ **Request Submitted! Payment Under 24 Hours.**")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 Approve", callback_data=f"wit_app_{m.chat.id}_{amt}"),
               types.InlineKeyboardButton("🔴 Reject", callback_data=f"wit_rej_{m.chat.id}_{amt}"))
    bot.send_message(WITHDRAWAL_CHANNEL_ID, f"🚨 **New Withdrawal Request**\n👤 User: `{m.chat.id}`\n💰 Amt: ₹{amt}\n📱 UPI: `{upi}`", parse_mode="Markdown", reply_markup=markup)

# --- CALLBACKS & PROOF ---
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    # Withdrawal Audit
    if c.data.startswith('wit_'):
        if c.from_user.id != ADMIN_ID: return
        act, uid, amt = c.data.split('_')[1], c.data.split('_')[2], c.data.split('_')[3]
        if act == "app":
            bot.edit_message_caption(f"🟢 **Approved! Paid ₹{amt}.**", c.message.chat.id, c.message.id)
            try: bot.send_message(uid, "🎉 **Whoo Hoo! Your Money Transferred In Your Wallet Check Now.**\nIf not received msg @Raka01")
            except: pass
        else:
            db = get_db()
            db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amt, uid))
            db.commit()
            db.close()
            bot.edit_message_caption(f"🔴 **Rejected! Returned ₹{amt} to Wallet.**", c.message.chat.id, c.message.id)
            try: bot.send_message(uid, "❌ **Your Withdrawal Rejected!**\nMoney returned to your wallet. Pls Withdraw again.")
            except: pass
    
    # Task Logic
    elif c.data == "single":
        db = get_db()
        task = db.execute('SELECT * FROM task_pool WHERE status="AVAILABLE" LIMIT 1').fetchone()
        if not task:
            bot.answer_callback_query(c.id, "⚠️ No task available!")
            return
        db.execute('UPDATE task_pool SET status="LOCKED" WHERE id=?', (task['id'],))
        db.commit()
        db.close()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Done", callback_data="task_done"), types.InlineKeyboardButton("❌ Cancel", callback_data="task_cancel"))
        bot.edit_message_text(f"📨 **Gmail:** `{task['gmail']}`\n🔑 **Pass:** `{task['password']}`", c.message.chat.id, c.message.id, parse_mode="Markdown", reply_markup=markup)
    
    elif c.data == "task_done":
        msg = bot.send_message(c.message.chat.id, "📸 **Screenshot bhejein proof ke liye:**")
        bot.register_next_step_handler(msg, verify_proof)

def verify_proof(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 Approve", callback_data="app"), types.InlineKeyboardButton("🔴 Reject", callback_data="rej"))
    bot.send_photo(PROOF_CHANNEL_ID, m.photo[-1].file_id, caption=f"🛰️ **New Proof from {m.chat.id}**", reply_markup=markup)
    bot.send_message(m.chat.id, "⏳ **Admin ko proof bhej diya gaya hai.**")

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['addtask', 'bulkadd', 'addbalance', 'broadcast'])
def admin_cmds(m):
    if m.chat.id != ADMIN_ID: return
    db = get_db()
    if m.text.startswith('/addtask'):
        d = m.text.replace('/addtask', '').split(':')
        db.execute('INSERT INTO task_pool (gmail, password) VALUES (?,?)', (d[0].strip(), d[1].strip()))
    elif m.text.startswith('/bulkadd'):
        for line in m.text.split('\n')[1:]:
            d = line.split(':')
            db.execute('INSERT INTO task_pool (gmail, password) VALUES (?,?)', (d[0].strip(), d[1].strip()))
    elif m.text.startswith('/addbalance'):
        d = m.text.split()
        db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (d[2], d[1]))
    db.commit()
    db.close()
    bot.reply_to(m, "✅ **Done!**")

bot.infinity_polling()
