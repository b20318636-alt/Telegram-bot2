import telebot
import sqlite3
import hashlib
import time
import random
import os
from telebot import types

# Use environment variable for the token to keep it secure
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    # For local testing, you can set it here, but it's better to use environment variables
    TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

DB_NAME = 'referral_bot.db'
CHANNEL_ID = -1003579124716  # User's channel ID
OWNER_ID = 7253742084
CONTACT_USERNAME = "Honestbanda"

# Button Labels (Exactly matching the user's screenshot)
BTN_START = "🚀 Start"
BTN_REF_LINK = "🔗 My Referral Link"
BTN_STATS = "📊 My Stats"
BTN_LEADERBOARD = "🏆 Leaderboard"
BTN_GIVEAWAYS = "🎁 Active Giveaways"
BTN_HALL_OF_FAME = "🌟 Hall of Fame"
BTN_CONTACT = "💰 For Profit ✅ Contact"
BTN_CASH_AGENT = "🔪👿 Cash Agent 👿🔪"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            referral_code TEXT UNIQUE,
            invite_link TEXT,
            points INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS giveaways (
            giveaway_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prize TEXT NOT NULL,
            end_time INTEGER NOT NULL,
            channel_message_id INTEGER,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS giveaway_participants (
            giveaway_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (giveaway_id, user_id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def get_user(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, referral_code, invite_link, points, referrals FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_invite_link(invite_link):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, referral_code, invite_link, points, referrals FROM users WHERE invite_link = ?', (invite_link,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"Error getting user by invite link: {e}")
        return None

def create_user(user_id, username, invite_link=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        referral_code = hashlib.sha1(str(user_id).encode()).hexdigest()[:8]
        cursor.execute('INSERT INTO users (user_id, username, referral_code, invite_link) VALUES (?, ?, ?, ?)',
                       (user_id, username, referral_code, invite_link))
        conn.commit()
        conn.close()
        return referral_code
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def update_user_invite_link(user_id, invite_link):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET invite_link = ? WHERE user_id = ?', (invite_link, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating invite link: {e}")

def add_referral_by_user_id(referrer_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET referrals = referrals + 1, points = points + 10 WHERE user_id = ?', (referrer_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error adding referral: {e}")

def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    # Row 1: Start
    keyboard.row(types.KeyboardButton(BTN_START))
    # Row 2: Referral Link and Stats
    keyboard.row(types.KeyboardButton(BTN_REF_LINK), types.KeyboardButton(BTN_STATS))
    # Row 3: Leaderboard and Giveaways
    keyboard.row(types.KeyboardButton(BTN_LEADERBOARD), types.KeyboardButton(BTN_GIVEAWAYS))
    # Row 4: Hall of Fame and Contact
    keyboard.row(types.KeyboardButton(BTN_HALL_OF_FAME), types.KeyboardButton(BTN_CONTACT))
    # Row 5: Cash Agent (Requested)
    keyboard.row(types.KeyboardButton(BTN_CASH_AGENT))
    return keyboard

@bot.message_handler(commands=['start'])
def command_start(message):
    handle_start(message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    # Unified handler for exact matching
    if text == BTN_START:
        handle_start(message)
    elif text == BTN_REF_LINK:
        handle_ref_link(message)
    elif text == BTN_STATS:
        handle_stats(message)
    elif text == BTN_LEADERBOARD:
        handle_leaderboard(message)
    elif text == BTN_GIVEAWAYS:
        handle_giveaways(message)
    elif text == BTN_HALL_OF_FAME:
        handle_hall_of_fame(message)
    elif text == BTN_CONTACT:
        handle_contact(message)
    elif text == BTN_CASH_AGENT:
        handle_cash_agent(message)
    else:
        # Default response for unknown text
        bot.send_message(message.chat.id, "Please use the menu buttons below:", reply_markup=main_menu_keyboard())

def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    if not user:
        create_user(user_id, username)
        
    welcome_text = (
        f"👋 *Hello {username}! Welcome to WinWon Referral Bot!* 🌟\n\n"
        "Earn rewards and climb the leaderboard by inviting your friends to our channel!\n\n"
        "🚀 *How to get started:*\n"
        "1️⃣ Click '🔗 *My Referral Link*' to get your unique link.\n"
        "2️⃣ Share it with friends! You get *10 points* for every join.\n"
        "3️⃣ Check '📊 *My Stats*' to see your progress.\n"
        "4️⃣ View '🏆 *Leaderboard*' to see top referrers.\n\n"
        "💰 *Business Inquiries?* Click '💰 *For Profit ✅ Contact*' to talk to the owner!\n\n"
        "👇 *Use the menu below to start earning!*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

def handle_ref_link(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user:
        invite_link = user[3]
        if not invite_link:
            try:
                new_link = bot.create_chat_invite_link(CHANNEL_ID, name=f"Referral_{user_id}").invite_link
                update_user_invite_link(user_id, new_link)
                invite_link = new_link
            except Exception as e:
                bot.send_message(message.chat.id, "❌ Error creating invite link. Make sure I am an admin in the channel!", reply_markup=main_menu_keyboard())
                print(f"Error creating invite link: {e}")
                return

        share_text = (
            f"📢 *Your Unique Channel Invite Link:*\n\n"
            f"`{invite_link}`\n\n"
            f"✨ *Share this link* to invite friends directly to our channel!\n"
            f"🎁 Earn *10 points* for each friend who joins.\n"
            f"🏆 More referrals = Higher chance to win giveaways!"
        )
        bot.send_message(message.chat.id, share_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

def handle_stats(message):
    user = get_user(message.from_user.id)
    if user:
        username, points, referrals = user[1], user[4], user[5]
        stats_text = (
            f"📊 *Your Personal Stats:*\n\n"
            f"👤 *Username:* @{username}\n"
            f"✨ *Total Points:* `{points}`\n"
            f"🤝 *Total Referrals:* `{referrals}`\n\n"
            f"🔥 Keep sharing to climb the leaderboard!"
        )
        bot.send_message(message.chat.id, stats_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        create_user(message.from_user.id, message.from_user.username or message.from_user.first_name)
        bot.send_message(message.chat.id, "Your profile has been created! Try clicking the button again.", reply_markup=main_menu_keyboard())

def handle_leaderboard(message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, referrals, points FROM users ORDER BY referrals DESC, points DESC LIMIT 10')
    top_users = cursor.fetchall()
    conn.close()

    if top_users:
        leaderboard_text = "🏆 *Top 10 Referrers Leaderboard* 🏆\n\n"
        for i, user in enumerate(top_users):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
            leaderboard_text += f"{medal} *{user[0]}* — `{user[1]}` referrals (`{user[2]}` pts)\n"
        bot.send_message(message.chat.id, leaderboard_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        bot.send_message(message.chat.id, "No users on the leaderboard yet. Be the first!", reply_markup=main_menu_keyboard())

def handle_hall_of_fame(message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, referrals FROM users ORDER BY referrals DESC LIMIT 3')
    top_3 = cursor.fetchall()
    conn.close()

    if top_3:
        hall_text = "🌟 *HALL OF FAME* 🌟\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, user in enumerate(top_3):
            hall_text += f"{medals[i]} *LEGEND:* @{user[0]}\n🔥 Referrals: `{user[1]}`\n\n"
        hall_text += "Will you be the next legend? 🚀"
        bot.send_message(message.chat.id, hall_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        bot.send_message(message.chat.id, "The Hall of Fame is empty. Start referring to claim your spot!", reply_markup=main_menu_keyboard())

def handle_giveaways(message):
    bot.send_message(message.chat.id, "🎁 *Check our channel for active giveaways!* 🎁", parse_mode="Markdown", reply_markup=main_menu_keyboard())

def handle_contact(message):
    contact_text = (
        f"💰 *For Profit & Business Inquiries* ✅\n\n"
        f"Please contact the owner directly: @{CONTACT_USERNAME}\n\n"
        f"🚀 Let's grow together!"
    )
    bot.send_message(message.chat.id, contact_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

def handle_cash_agent(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("💸 Contact Cash Agent 💸", url=f"https://t.me/{CONTACT_USERNAME}")
    markup.add(btn)
    
    bot.send_message(
        message.chat.id, 
        "🔪👿 *Welcome to the Cash Agent!* 👿🔪\n\nClick the button below to connect directly with the agent for all cash transactions and inquiries.",
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.send_message(message.chat.id, "👇 *Main Menu*", reply_markup=main_menu_keyboard())

@bot.chat_member_handler()
def on_chat_member_update(update):
    if update.chat.id == CHANNEL_ID:
        if update.old_chat_member.status in ['left', 'kicked'] and update.new_chat_member.status in ['member', 'administrator', 'creator']:
            invite_link = update.invite_link.invite_link if update.invite_link else None
            if invite_link:
                referrer = get_user_by_invite_link(invite_link)
                if referrer:
                    referrer_id = referrer[0]
                    referrer_name = referrer[1]
                    new_member_name = update.new_chat_member.user.first_name
                    
                    add_referral_by_user_id(referrer_id)
                    
                    # Meme-style celebration messages
                    meme_messages = [
                        f"🔥 *STOCKS GOING UP!* 🔥\n\n🚀 *{new_member_name}* just joined the gang!\n🤝 Big brain move by *{referrer_name}*! +10 Points! 📈",
                        f"💎 *DIAMOND HANDS!* 💎\n\nWelcome *{new_member_name}* to the moon! 🌕\nReferrer *{referrer_name}* is collecting those points! 💰",
                        f"😎 *CHAD MOVE DETECTED!* 😎\n\n*{new_member_name}* is in the house!\n*{referrer_name}* is on fire! 🔥 +10 Points!",
                        f"🎉 *WE GOT A LIVE ONE!* 🎉\n\n*{new_member_name}* joined the community!\nShoutout to *{referrer_name}* for the invite! 🏆",
                        f"🚀 *TO THE MOON!* 🚀\n\n*{new_member_name}* has landed!\n*{referrer_name}* is climbing the leaderboard! 🥇"
                    ]
                    celebration_text = random.choice(meme_messages)
                    
                    try:
                        bot.send_message(CHANNEL_ID, celebration_text, parse_mode="Markdown")
                        bot.send_message(referrer_id, f"🎊 *Cha-Ching!* 🎊\n\nYour friend *{new_member_name}* just joined! You earned *10 points*! 📈", parse_mode="Markdown")
                    except Exception as e:
                        print(f"Error sending celebration: {e}")

if __name__ == '__main__':
    init_db()
    print("Bot started...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, allowed_updates=["message", "callback_query", "chat_member"])
        except Exception as e:
            print(f"Polling error: {e}. Restarting in 15 seconds...")
            time.sleep(15)
