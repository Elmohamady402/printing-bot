"""
🤖 بوت تليجرام للمكتبة - نظام طباعة للطلاب

المميزات:
- عرض الملفات المتاحة من files_config.json
- نظام رصيد للطلاب
- شحن رصيد عبر فودافون كاش
- أرقام طلبات للاستلام
- حفظ البيانات تلقائياً

📝 لإضافة ملفات جديدة:
   عدّل ملف files_config.json وأعد تشغيل البوت
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import json
import os
from datetime import datetime

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token البوت
TOKEN = "8568624171:AAH5g55aZeti7ZuBSoOWyCTwC0VcxT3j0X4"

# الإعدادات
PRICE_PER_PAGE = 0.50  # سعر الورقة
MIN_CHARGE = 50  # الحد الأدنى للشحن

# حالات المحادثة
WAITING_FOR_RECEIPT = 1

# قاعدة البيانات (ملف JSON بسيط)
DATA_FILE = "bot_data.json"
FILES_CONFIG = "files_config.json"

def load_files_config():
    """تحميل تكوين الملفات"""
    if os.path.exists(FILES_CONFIG):
        with open(FILES_CONFIG, 'r', encoding='utf-8') as f:
            return json.load(f)
    # ملفات افتراضية لو الملف مش موجود
    return {
        "respiratory_system": {
            "name": "Respiratory System",
            "pages": 10,
            "price": 5.0
        }
    }

def load_data():
    """تحميل البيانات من الملف"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "users": {},
            "files": {},
            "orders": []
        }
    
    # تحميل الملفات من files_config.json
    data["files"] = load_files_config()
    return data

def save_data(data):
    """حفظ البيانات في الملف"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات
data = load_data()

def get_user_balance(user_id):
    """الحصول على رصيد المستخدم"""
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"balance": 0, "orders": []}
        save_data(data)
    return data["users"][user_id]["balance"]

def update_balance(user_id, amount):
    """تحديث رصيد المستخدم"""
    user_id = str(user_id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"balance": 0, "orders": []}
    data["users"][user_id]["balance"] += amount
    save_data(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    user = update.effective_user
    balance = get_user_balance(user.id)
    
    keyboard = [
        [InlineKeyboardButton("📚 عرض الملفات المتاحة", callback_data="show_files")],
        [InlineKeyboardButton("💰 شحن رصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("💳 رصيدي", callback_data="check_balance")],
        [InlineKeyboardButton("📋 طلباتي", callback_data="my_orders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
أهلاً بيك يا {user.first_name} في بوت المكتبة! 📚

رصيدك الحالي: {balance:.2f} جنيه

اختار من القائمة:
    """
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_files":
        await show_files(query, context)
    elif query.data == "charge_balance":
        await charge_balance_info(query, context)
    elif query.data == "check_balance":
        await check_balance(query, context)
    elif query.data == "my_orders":
        await show_my_orders(query, context)
    elif query.data.startswith("order_"):
        await process_order(query, context)
    elif query.data == "back_to_menu":
        await back_to_menu(query, context)

async def show_files(query, context):
    """عرض الملفات المتاحة"""
    files_text = "📚 *الملفات المتاحة للطباعة:*\n\n"
    
    keyboard = []
    for file_id, file_info in data["files"].items():
        files_text += f"📄 *{file_info['name']}*\n"
        files_text += f"   عدد الصفحات: {file_info['pages']}\n"
        files_text += f"   السعر: {file_info['price']:.2f} جنيه\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"🖨️ طباعة {file_info['name']}", 
            callback_data=f"order_{file_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(files_text, reply_markup=reply_markup, parse_mode='Markdown')

async def process_order(query, context):
    """معالجة الطلب"""
    user_id = str(query.from_user.id)
    file_id = query.data.replace("order_", "")
    
    if file_id not in data["files"]:
        await query.edit_message_text("❌ الملف غير موجود!")
        return
    
    file_info = data["files"][file_id]
    user_balance = get_user_balance(query.from_user.id)
    
    if user_balance < file_info["price"]:
        keyboard = [[InlineKeyboardButton("💰 شحن رصيد", callback_data="charge_balance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ رصيدك غير كافي!\n\n"
            f"رصيدك الحالي: {user_balance:.2f} جنيه\n"
            f"سعر الملف: {file_info['price']:.2f} جنيه\n"
            f"محتاج: {file_info['price'] - user_balance:.2f} جنيه إضافية",
            reply_markup=reply_markup
        )
        return
    
    # خصم المبلغ
    update_balance(query.from_user.id, -file_info["price"])
    
    # إنشاء رقم الطلب
    order_number = len(data["orders"]) + 1
    order = {
        "order_number": order_number,
        "user_id": user_id,
        "file_name": file_info["name"],
        "pages": file_info["pages"],
        "price": file_info["price"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "قيد الطباعة"
    }
    
    data["orders"].append(order)
    if user_id not in data["users"]:
        data["users"][user_id] = {"balance": 0, "orders": []}
    data["users"][user_id]["orders"].append(order_number)
    save_data(data)
    
    # رسالة التأكيد
    keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    new_balance = get_user_balance(query.from_user.id)
    
    await query.edit_message_text(
        f"✅ *تم الطلب بنجاح!*\n\n"
        f"📋 رقم الطلب: *{order_number}*\n"
        f"📄 الملف: {file_info['name']}\n"
        f"📃 عدد الصفحات: {file_info['pages']}\n"
        f"💵 المبلغ المدفوع: {file_info['price']:.2f} جنيه\n"
        f"💰 رصيدك المتبقي: {new_balance:.2f} جنيه\n\n"
        f"🏃 استلم طلبك من المكتبة برقم الطلب: *{order_number}*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def charge_balance_info(query, context):
    """معلومات شحن الرصيد"""
    keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 *لشحن رصيدك:*\n\n"
        f"1️⃣ حول على فودافون كاش\n"
        f"2️⃣ الحد الأدنى للشحن: {MIN_CHARGE} جنيه\n"
        f"3️⃣ بعد التحويل، ابعت صورة الإيصال هنا\n"
        f"4️⃣ هيتم مراجعة الطلب وشحن رصيدك\n\n"
        f"📱 *رقم فودافون كاش:* سيتم إرساله في رسالة خاصة\n\n"
        f"ملحوظة: الشحن يتم يدوياً خلال 24 ساعة",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # بدء المحادثة لاستقبال الإيصال
    context.user_data['awaiting_receipt'] = True

async def check_balance(query, context):
    """عرض الرصيد"""
    balance = get_user_balance(query.from_user.id)
    
    keyboard = [
        [InlineKeyboardButton("💰 شحن رصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💳 *رصيدك الحالي:* {balance:.2f} جنيه",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_my_orders(query, context):
    """عرض طلبات المستخدم"""
    user_id = str(query.from_user.id)
    
    if user_id not in data["users"] or not data["users"][user_id]["orders"]:
        keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📋 ليس لديك طلبات بعد", reply_markup=reply_markup)
        return
    
    orders_text = "📋 *طلباتك:*\n\n"
    for order_num in data["users"][user_id]["orders"]:
        order = next((o for o in data["orders"] if o["order_number"] == order_num), None)
        if order:
            orders_text += f"🔢 رقم الطلب: *{order['order_number']}*\n"
            orders_text += f"📄 الملف: {order['file_name']}\n"
            orders_text += f"💵 السعر: {order['price']:.2f} جنيه\n"
            orders_text += f"📅 التاريخ: {order['date']}\n"
            orders_text += f"✅ الحالة: {order['status']}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(orders_text, reply_markup=reply_markup, parse_mode='Markdown')

async def back_to_menu(query, context):
    """العودة للقائمة الرئيسية"""
    user = query.from_user
    balance = get_user_balance(user.id)
    
    keyboard = [
        [InlineKeyboardButton("📚 عرض الملفات المتاحة", callback_data="show_files")],
        [InlineKeyboardButton("💰 شحن رصيد", callback_data="charge_balance")],
        [InlineKeyboardButton("💳 رصيدي", callback_data="check_balance")],
        [InlineKeyboardButton("📋 طلباتي", callback_data="my_orders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
أهلاً بيك يا {user.first_name} في بوت المكتبة! 📚

رصيدك الحالي: {balance:.2f} جنيه

اختار من القائمة:
    """
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال صور الإيصالات"""
    user = update.effective_user
    
    # حفظ معلومات الإيصال للمراجعة
    receipt_info = {
        "user_id": str(user.id),
        "username": user.username or user.first_name,
        "photo_id": update.message.photo[-1].file_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # حفظ في ملف منفصل للمراجعة
    if os.path.exists("pending_receipts.json"):
        with open("pending_receipts.json", 'r', encoding='utf-8') as f:
            receipts = json.load(f)
    else:
        receipts = []
    
    receipts.append(receipt_info)
    with open("pending_receipts.json", 'w', encoding='utf-8') as f:
        json.dump(receipts, f, ensure_ascii=False, indent=2)
    
    await update.message.reply_text(
        "✅ تم استلام الإيصال!\n\n"
        "⏳ سيتم مراجعته وشحن رصيدك خلال 24 ساعة\n"
        "شكراً لك! 🙏"
    )

def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # تشغيل البوت
    print("🚀 البوت شغال الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
