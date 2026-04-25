from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

INTERESTS = [
    "🔬 Ilmiy-tadqiqot yo'nalishi",
    "💡 Innovatsion va startap loyihalar yo'nalishi",
    "🎯 Liderlik va shaxsiy rivojlanish yo'nalishi",
    "🧠 Intellektual va madaniy-ma'rifiy yo'nalish",
    "📢 Axborot va targ'ibot yo'nalishi",
]


def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Ariza topshirish")]],
        resize_keyboard=True
    )


def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )


def interests_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=i)] for i in INTERESTS],
        resize_keyboard=True
    )


def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="app_confirm")],
        [InlineKeyboardButton(text="✏️ Tahrirlash",  callback_data="app_edit")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="app_cancel")],
    ])


def edit_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 To'liq ism",   callback_data="ed_full_name")],
        [InlineKeyboardButton(text="🏫 Fakultet",      callback_data="ed_fakultet")],
        [InlineKeyboardButton(text="📚 Yo'nalish",     callback_data="ed_yonalish")],
        [InlineKeyboardButton(text="👥 Guruh",         callback_data="ed_guruh")],
        [InlineKeyboardButton(text="📞 Telefon",       callback_data="ed_phone")],
        [InlineKeyboardButton(text="🎯 Qiziqish",      callback_data="ed_interest")],
        [InlineKeyboardButton(text="🔙 Orqaga",        callback_data="ed_back")],
    ])


def interview_reply_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Kelaman",        callback_data="iv_yes")],
        [InlineKeyboardButton(text="❌ Kela olmayman",  callback_data="iv_no")],
    ])


def interview_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, yuborish",  callback_data="iv_send")],
        [InlineKeyboardButton(text="❌ Bekor qilish",  callback_data="iv_cancel")],
    ])


def admin_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Arizalar ro'yxati"),
             KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="📅 Suhbat belgilash"),
             KeyboardButton(text="📤 Excel eksport")],
        ],
        resize_keyboard=True
    )
