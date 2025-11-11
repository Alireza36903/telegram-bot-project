from telegram import ReplyKeyboardMarkup

def get_membership_keyboard():
    keyboard = [["🗿 الان میرم عضو می‌شم"], ["✅ عضو شده‌ام"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_keyboard():
    keyboard = [
        ["🕹️ ایتم‌ها", "🎙️ آموزش‌ها"],
        ["🪪 حساب کاربری"],
        ["📊 تابلوی امتیازات", "🔐 فیلتر شکن"],
        ["🖥️ windows"],
        ["📬 پیشنهادات", "🧾 درباره ما"],
        ["💻 ادمین"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_decision_keyboard():
    keyboard = [
        ["Never mind✅"],
        ["Block account❌"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_confirmation_keyboard():
    keyboard = [
        ["🏠 بازگشت"],
        ["بله کاملا مطمئنم.✅"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ton_leaderboard_keyboard():
    keyboard = [
        ["🔋 TONهای من", "🧲 کسب TON"],
        ["📊 نظرسنجی‌های من"],
        ["🏠 بازگشت به منوی اصلی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_surveys_keyboard():
    keyboard = [
        ["نظرسنجی‌های انجام شده.✅"],
        ["🏠 بازگشت به منوی اصلی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_survey_details_keyboard():
    keyboard = [
        ["نظرسنجی های درست🔋", "نظرسنجی های نادرست 🪫"],
        ["🔙 بازگشت"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_earn_ton_keyboard():
    keyboard = [
        ["⚒️ استخراج", "🪧 راهنما"],
        ["🔙 بازگشت"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
