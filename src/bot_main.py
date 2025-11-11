import logging
import datetime
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from database import *
from keyboards import *

# تنظیمات از Environment Variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '8337570936:AAFRSYOu8LQvv18om2N1xsLorHCeApTWAFo')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@linkGameETC')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6243728824'))
MAX_WARNINGS = 4
MAX_TON = 750

# راه‌اندازی لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)

# چک کردن عضویت در کانال
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"خطا در چک عضویت کاربر {user_id}: {e}")
        return False

# ارسال نوتیف به ادمین برای کاربر بلاک شده
async def send_block_notification(user_id, context):
    username, first_name, warning_count = get_user_info(user_id)
    
    admin_message = (
        f"⚠️ آقای Alireza\n\n"
        f"یک کاربر با مشخصات زیر {warning_count} بار تلاش کرده بدون دنبال کردن از من استفاده کنه:\n\n"
        f"👤 نام: {first_name or 'بدون نام'}\n"
        f"🆔 آیدی: @{username or 'بدون آیدی'}\n"
        f"🔢 آیدی عددی: {user_id}\n"
        f"⚠️ تعداد هشدارها: {warning_count}\n\n"
        f"واکنش شما چیه؟"
    )
    
    context.user_data['pending_admin_action'] = user_id
    context.user_data['pending_user_info'] = {
        'username': username,
        'first_name': first_name,
        'user_id': user_id
    }
    
    # ارسال پیام به کاربر بلاک شده
    try:
        user_message = "⚠️ کاربر گرامی رفتار نادرست شما به ادمین ارسال شد.📨\nاگر تایید شد از بایگانی خارج می‌شوید، در غیر این صورت از خدمات رسانی ربات به شما معذوریم."
        await context.bot.send_message(user_id, user_message)
    except Exception as e:
        logger.error(f"خطا در ارسال پیام به کاربر بلاک شده: {e}")
    
    await context.bot.send_message(ADMIN_ID, admin_message, reply_markup=get_admin_decision_keyboard())

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if is_user_blocked(user.id):
        blocked_message = "⛔ حساب شما مسدود شده است. لطفاً با ادمین تماس بگیرید."
        await update.message.reply_text(blocked_message)
        return
    
    is_new_user = add_or_update_user(user.id, user.username, user.first_name, user.last_name)
    
    if is_new_user:
        admin_message = (
            f"👤 کاربر جدید:\n"
            f"نام: {user.first_name or 'بدون نام'}\n"
            f"آیدی: @{user.username or 'بدون آیدی'}\n"
            f"آیدی عددی: {user.id}\n"
            f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        try:
            await context.bot.send_message(ADMIN_ID, admin_message)
        except Exception as e:
            logger.error(f"خطا در ارسال نوتیف به ادمین: {e}")
    
    welcome_message = "🍃 دوست من لطفاً به کانال اصلی ما ملحق شوید."
    await update.message.reply_text(welcome_message, reply_markup=get_membership_keyboard())

# هندلر پیام‌های کاربران عادی
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text

    if is_user_blocked(user.id):
        blocked_message = "⛔ حساب شما مسدود شده است. لطفاً با ادمین تماس بگیرید."
        await update.message.reply_text(blocked_message)
        return

    if message_text == "✅ عضو شده‌ام":
        is_member = await check_channel_membership(user.id, context)
      if is_member:
            user_balance = get_user_balance(user.id)
            current_time = datetime.datetime.now().strftime("%Y/%m/%d ← ⏰ %H:%M:%S")
            
            status_message = (
                f"👨‍💻 وضعیت حساب کاربری شما\n\n"
                f"👤 نام: {user.first_name or 'بدون نام'}\n"
                f"🥷 شناسه کاربری: {user.id}\n"
                f"💰 موجودی توکن: {user_balance} TON\n"
                f"📆 {current_time}\n\n"
                f"---------------------\n"
                f"شما با ورودتون 200 TON دریافت کردید.🎉\n"
                f"با این TON ها میتونید فایل دانلود کنید یا هر خدمات دیگر.\n\n"
                f"چجوری TON جمع کنیم؟🤔\n"
                f"هر نظرسنجی که در کانال قرار داده می‌شود شما می‌توانید با زدن گزینه درست صاحب 10 TON شوید ! ✅\n\n"
                f"برای رفع شدن سوالات شما از دو طریق می‌تونید نظرات و سوالاتون رو مطرح کنید⚡\n"
                f"1. درباره ما ← سوالات متداول ✅\n"
                f"2. پیشنهادات ← نظرتون و سوالاتون مستقیم به ادمین ارسال می‌شود ✅"
            )
            await update.message.reply_text(status_message, reply_markup=get_main_keyboard())
        else:
            warning_count = increment_warning_count(user.id)
            warning_message = "⚠️ رفیق من برای اینکه به من دسترسی پیدا کنید لطفاً کانال مارا دنبال کنید."
            await update.message.reply_text(warning_message, reply_markup=get_membership_keyboard())
            
            if warning_count >= MAX_WARNINGS:
                block_user(user.id)
                await send_block_notification(user.id, context)

    elif message_text == "🗿 الان میرم عضو می‌شم":
        channel_message = f"👋 لینک کانال: {CHANNEL_USERNAME}\n\nپس از عضویت، گزینه '✅ عضو شده‌ام' را انتخاب کنید."
        await update.message.reply_text(channel_message, reply_markup=get_membership_keyboard())

    else:
        unknown_message = "⚠️ رفیق من، لطفاً از گزینه‌های زیر استفاده کن: '🗿 الان میرم عضو می‌شم' یا '✅ عضو شده‌ام'."
        await update.message.reply_text(unknown_message, reply_markup=get_membership_keyboard())

# هندلر تابلوی امتیازات و کسب TON
async def handle_ton_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text

    if message_text == "📊 تابلوی امتیازات":
        welcome_message = "درود به قسمت تابلوی امتیازات خوش آمدید!\nمیتونم کمکتون کنم؟"
        await update.message.reply_text(welcome_message, reply_markup=get_ton_leaderboard_keyboard())

    elif message_text == "🧲 کسب TON":
        await update.message.reply_text("بخش کسب TON", reply_markup=get_earn_ton_keyboard())

    elif message_text == "📊 نظرسنجی‌های من":
        surveys_message = "شما به بخش نظرسنجی‌های من آمدید."
        await update.message.reply_text(surveys_message, reply_markup=get_surveys_keyboard())

    elif message_text == "نظرسنجی‌های انجام شده.✅":
        await update.message.reply_text("جزئیات نظرسنجی‌های شما:", reply_markup=get_survey_details_keyboard())

    elif message_text == "نظرسنجی های درست🔋":
        stats = get_user_survey_stats(user.id)
        correct_surveys = stats['correct_surveys']
        ton_earned = correct_surveys * 10
        
        current_balance = get_user_balance(user.id)
        new_balance = min(current_balance + ton_earned, MAX_TON)
        update_user_balance(user.id, new_balance)
        
        success_message = (
            f"دوست عزیز شما با {correct_surveys} بار انجام دادن نظرسنجی درست\n"
            f"توانستید {ton_earned} TON به دست آورید.\n\n"
            f"⚠️ نکته ⚠️\n"
            f"برای اینکه بتوانید این TON هایتان را استخراج کنید باید به بخش • کسب TON • بروید.💰"
        )
        
        await update.message.reply_text(success_message, reply_markup=get_survey_details_keyboard())

    elif message_text == "نظرسنجی های نادرست 🪫":
      elif message_text == "🏠 بازگشت به منوی اصلی":
        await update.message.reply_text("بازگشت به منوی اصلی", reply_markup=get_main_keyboard())

# هندلر پیام‌های ادمین
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text
    
    if user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی denied.")
        return
    
    if 'pending_admin_action' in context.user_data:
        target_user_id = context.user_data['pending_admin_action']
        user_info = context.user_data['pending_user_info']
        
        if message_text == "Never mind✅":
            if 'awaiting_confirmation' in context.user_data:
                unblock_user(target_user_id)
                await update.message.reply_text(f"✅ کاربر {user_info['first_name']} (@{user_info['username']}) آنبلاک شد.", reply_markup=get_main_keyboard())
                
                try:
                    unblock_message = "سلام شما اکنون می‌توانید از خدمات رسانی من استفاده کنید.✅"
                    await context.bot.send_message(target_user_id, unblock_message)
                except Exception as e:
                    logger.error(f"خطا در ارسال پیام آنبلاک به کاربر: {e}")
                
                context.user_data.clear()
            else:
                context.user_data['awaiting_confirmation'] = 'unblock'
                await update.message.reply_text("⚠️ آیا از این انتخاب اطمینان دارید؟⚠️", reply_markup=get_admin_confirmation_keyboard())
                
        elif message_text == "Block account❌":
            if 'awaiting_confirmation' in context.user_data:
                block_user(target_user_id)
                await update.message.reply_text(f"❌ کاربر {user_info['first_name']} (@{user_info['username']}) بلاک شد.", reply_markup=get_main_keyboard())
                
                try:
                    block_message = "سلام ما قادر به خدمات رسانی شما نیستیم.❌"
                    await context.bot.send_message(target_user_id, block_message)
                except Exception as e:
                    logger.error(f"خطا در ارسال پیام بلاک به کاربر: {e}")
                
                context.user_data.clear()
            else:
                context.user_data['awaiting_confirmation'] = 'block'
                await update.message.reply_text("⚠️ آیا از این انتخاب اطمینان دارید؟⚠️", reply_markup=get_admin_confirmation_keyboard())
                
        elif message_text == "🏠 بازگشت":
            if 'awaiting_confirmation' in context.user_data:
                del context.user_data['awaiting_confirmation']
            await update.message.reply_text("بازگشت به منوی مدیریت...", reply_markup=get_admin_decision_keyboard())
            
        elif message_text == "بله کاملا مطمئنم.✅":
            action_type = context.user_data.get('awaiting_confirmation')
            if action_type == 'unblock':
                unblock_user(target_user_id)
                await update.message.reply_text(f"✅ کاربر {user_info['first_name']} (@{user_info['username']}) آنبلاک شد.", reply_markup=get_main_keyboard())
                
                try:
                    unblock_message = "سلام شما اکنون می‌توانید از خدمات رسانی من استفاده کنید.✅"
                    await context.bot.send_message(target_user_id, unblock_message)
                except Exception as e:
                    logger.error(f"خطا در ارسال پیام آنبلاک به کاربر: {e}")
                    
            elif action_type == 'block':
                block_user(target_user_id)
                await update.message.reply_text(f"❌ کاربر {user_info['first_name']} (@{user_info['username']}) بلاک شد.", reply_markup=get_main_keyboard())
                
                try:
                    block_message = "سلام ما قادر به خدمات رسانی شما نیستیم.❌"
                  stats = get_user_survey_stats(user.id)
        
        stats_message = (
            f"🥷 نام: {user.first_name or 'بدون نام'}\n"
            f"😎 تعداد نظرسنجی‌های کل شما: {stats['total_surveys']}\n"
            f"🤕 تعداد نظر سنجی‌های نادرست شما: {stats['incorrect_surveys']}\n"
            f"🤩 امتیاز منفی تعلق نمی‌گیرد."
        )
        
        await update.message.reply_text(stats_message, reply_markup=get_survey_details_keyboard())

    elif message_text == "🔋 TONهای من":
        purchases = get_user_purchases(user.id)
        
        if not purchases:
            no_purchases_message = "📭 شما هنوز هیچ فایلی خریداری نکرده‌اید."
            await update.message.reply_text(no_purchases_message, reply_markup=get_ton_leaderboard_keyboard())
            return
        
        purchases_message = "📋 فایل‌های خریداری شده توسط شما:\n\n"
        total_spent = 0
        
        for i, purchase in enumerate(purchases, 1):
            file_name, file_category, ton_cost, purchase_date, download_count = purchase
            purchases_message += f"{i}. {file_name}\n"
            purchases_message += f"   📁 دسته: {file_category}\n"
            purchases_message += f"   💰 هزینه: {ton_cost} TON\n"
            purchases_message += f"   📅 تاریخ: {purchase_date}\n"
            purchases_message += f"   📥 تعداد دانلود: {download_count} بار\n\n"
            total_spent += ton_cost
        
        purchases_message += f"💰 مجموع هزینه‌ها: {total_spent} TON"
        
        await update.message.reply_text(purchases_message)
        await update.message.reply_text("بازگشت به تابلوی امتیازات", reply_markup=get_ton_leaderboard_keyboard())

    elif message_text == "⚒️ استخراج":
        await update.message.reply_text("شما به بخش استخراج TON وارد شدید!")
        
        stats = get_user_survey_stats(user.id)
        user_balance = get_user_balance(user.id)
        
        table = (
            "-------------------\n"
            f"نام : {user.first_name or 'بدون نام'}\n"
            f"نظرسنجی درست : {stats['correct_surveys']}\n"
            f"نظرسنجی نادرست : {stats['incorrect_surveys']}\n"
            f"موجودی TON : {user_balance}\n"
            f"قابل برداشت : {user_balance}\n"
            "-------------------"
        )
        
        await update.message.reply_text(table)
        await update.message.reply_text("بازگشت به بخش کسب TON", reply_markup=get_earn_ton_keyboard())

    elif message_text == "🪧 راهنما":
        guide_text = (
            "در اینجا به شما آموزش می‌دهیم که چگونه TON کسب کنید.\n\n"
            "سوال: اصلاً چرا ما باید به TON نیاز داشته باشیم؟\n"
            "زمانی ما به آن نیاز پیدا می‌کنیم که می‌خواهیم فایلی از یک آیتم یا به طور دیگر برای مثال: ما برای دانلود فایل DLC ماین کرافت بدراک یا هر چیز دیگری به مقداری TON نیاز داریم. هر فایلی که در کانال قرار می‌گیرد، مقدار TON اون فایل مشخص می‌شود.\n\n"
            "ما در کانال فایلی قرار نمی‌دهیم فقط تصاویر یا ویدیو کوتاهی از اون آموزش یا فیلم را برای شما قرار می‌دهیم و مقدار TON آن را ذکر می‌کنیم شما برای اینکه بتوانید فایل اون عکس مد نظرتون رو دانلود کنید در قسمت آیتم‌ها نوع اون عکس را مشخص می‌کنید. یعنی اگه اون عکسی که در کانال قرار گرفته مربوط به بازی‌های PC هست شما با باز کردن منوی آیتم‌ها و زدن روی گزینه PC می‌توانید نام آن فایل را از کانال کپی کنید و به ربات بدهید ربات اول از شما می‌پرسد که آیا می‌خواهید برای دانلود این فایل X مقدار TON بدهید؟ در ادامه اگر شما تایید کنید ربات اون مقدار TON را از موجودی شما کم می‌کند، و به شما فایل 💾 مد نظر را می‌دهد.\n\n"
            "اگر در این بازه مشکلی داشتید و نیاز به راهنمای بیشتر داشتید میتوانید در منو اصلی روی گزینه ادمین کلیک کنید 🆗 و در قسمت • راهنمایی • مشکل خودتون رو با ادمین در میان بذارید 🎙️\n\n"
            "با تشکر."
        )
        
        await update.message.reply_text(guide_text, reply_markup=get_earn_ton_keyboard())

    elif message_text == "🔙 بازگشت":
        await update.message.reply_text("بازگشت به تابلوی امتیازات", reply_markup=get_ton_leaderboard_keyboard())
await context.bot.send_message(target_user_id, block_message)
                except Exception as e:
                    logger.error(f"خطا در ارسال پیام بلاک به کاربر: {e}")
            
            context.user_data.clear()

def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.User(ADMIN_ID), 
        handle_user_message
    ))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), 
        handle_admin_message
    ))
    
    application.add_handler(MessageHandler(
        filters.Text([
            "📊 تابلوی امتیازات", "📊 نظرسنجی‌های من", "نظرسنجی‌های انجام شده.✅", 
            "نظرسنجی های درست🔋", "نظرسنجی های نادرست 🪫", "🔙 بازگشت", 
            "🏠 بازگشت به منوی اصلی", "🔋 TONهای من", "🧲 کسب TON",
            "⚒️ استخراج", "🪧 راهنما"
        ]) & ~filters.COMMAND,
        handle_ton_leaderboard
    ))
    
    logger.info("🤖 ربات فعال شد...")
    application.run_polling()

if name == 'main':
    main()
