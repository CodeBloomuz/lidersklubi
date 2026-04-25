import os
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command

import database as db
import keyboards as kb
from keyboards import INTERESTS
from docx_gen import generate, make_initial
from config import ADMIN_IDS

router = Router()
log = logging.getLogger(__name__)

# ── States ────────────────────────────────────────────────────────────────────

class Form(StatesGroup):
    full_name   = State()
    fakultet    = State()
    yonalish    = State()
    guruh       = State()
    phone       = State()
    interest    = State()
    confirm     = State()
    doc_upload  = State()   # imzolangan doc kutilmoqda

class Edit(StatesGroup):
    waiting = State()

# ── Helpers ───────────────────────────────────────────────────────────────────

def preview(d: dict) -> str:
    fish    = d["full_name"]
    initial = make_initial(fish)
    return (
        f"<i>Termiz iqtisodiyot va servis universiteti\n"
        f"rektori A.E.Absamatovga\n"
        f"{d['fakultet']}\n"
        f"{d['yonalish']} {d['guruh']}-guruh talabasi\n"
        f"{fish} tomonidan</i>\n\n"
        f"<b>ARIZA</b>\n\n"
        f"Men <b>{fish}</b> Termiz iqtisodiyot va servis "
        f"universitetida tashkil etilgan \"Intellectual Leaders Club\"ga "
        f"a'zolikka qabul qilish bo'yicha o'tkaziladigan tanlovda ishtirok "
        f"etishimga ruxsat berishingizni so'rayman.\n\n"
        f"<i>{d['guruh']}-guruh talabasi          {initial}</i>"
    )

# ── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    existing = await db.get_applicant(message.from_user.id)
    if existing:
        await message.answer(
            f"Salom, <b>{existing['full_name'].split()[0]}</b>! 👋\n\n"
            f"Siz allaqachon ariza topshirgansiz.\n"
            f"Ariza holati: /mystatus",
            parse_mode="HTML",
            reply_markup=kb.main_kb()
        )
        return
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "🎓 <b>Intellectual Leaders Club</b>ga xush kelibsiz!\n\n"
        "Bu klub orqali:\n"
        "🔬 Ilmiy tadqiqot imkoniyatlari\n"
        "💡 Innovatsion g'oyalar va startaplar\n"
        "🎯 Liderlik ko'nikmalarini rivojlantirish\n"
        "🧠 Intellektual rivojlanish\n"
        "📢 Axborot va targ'ibot\n\n"
        "A'zo bo'lish uchun ariza topshiring! 👇",
        parse_mode="HTML",
        reply_markup=kb.main_kb()
    )

# ── /mystatus ─────────────────────────────────────────────────────────────────

@router.message(Command("mystatus"))
async def cmd_mystatus(message: Message):
    u = await db.get_applicant(message.from_user.id)
    if not u:
        await message.answer("Siz hali ariza topshirgansiz. /start")
        return
    reply_map = {
        "yes": "✅ Suhbatga kelishingizni tasdiqladingiz",
        "no":  "❌ Suhbatga kela olmasligingizni bildirdingiz",
        None:  "⏳ Suhbat haqida xabar kutilmoqda",
    }
    await message.answer(
        f"📋 <b>Ariza ma'lumotlari</b>\n\n"
        f"👤 {u['full_name']}\n"
        f"🏫 {u['fakultet']}\n"
        f"📚 {u['yonalish']}\n"
        f"👥 Guruh: {u['guruh']}\n"
        f"📞 {u['phone']}\n"
        f"🎯 {u['interest']}\n\n"
        f"📌 Holat: {reply_map.get(u['interview_reply'])}",
        parse_mode="HTML"
    )

# ── Ariza boshlash ────────────────────────────────────────────────────────────

@router.message(F.text == "📝 Ariza topshirish")
async def start_form(message: Message, state: FSMContext):
    if await db.get_applicant(message.from_user.id):
        await message.answer("Siz allaqachon ariza topshirgansiz. /mystatus")
        return
    await state.set_state(Form.full_name)
    await message.answer(
        "<b>1/6</b> — To'liq ismingizni kiriting\n"
        "<i>Familya Ism Otasining ismi</i>\n\n"
        "Misol: <code>Toshtemirov Dilmurod Xasanovich</code>",
        parse_mode="HTML",
        reply_markup=kb.cancel_kb()
    )

# ── Savol-javob ───────────────────────────────────────────────────────────────

@router.message(Form.full_name)
async def q_full_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(Form.fakultet)
    await message.answer(
        "<b>2/6</b> — Fakultetingizni kiriting:\n"
        "<i>Misol: Iqtisodiyot va axborot texnologiyalari fakulteti</i>",
        parse_mode="HTML"
    )

@router.message(Form.fakultet)
async def q_fakultet(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return
    await state.update_data(fakultet=message.text.strip())
    await state.set_state(Form.yonalish)
    await message.answer(
        "<b>3/6</b> — Ta'lim yo'nalishingizni kiriting:\n"
        "<i>Misol: Iqtisodiyot</i>",
        parse_mode="HTML"
    )

@router.message(Form.yonalish)
async def q_yonalish(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return
    await state.update_data(yonalish=message.text.strip())
    await state.set_state(Form.guruh)
    await message.answer(
        "<b>4/6</b> — Guruhingizni kiriting:\n"
        "<i>Misol: IQT-4-23</i>",
        parse_mode="HTML"
    )

@router.message(Form.guruh)
async def q_guruh(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return
    await state.update_data(guruh=message.text.strip())
    await state.set_state(Form.phone)
    await message.answer(
        "<b>5/6</b> — Telefon raqamingizni kiriting:\n"
        "<i>Misol: +998901234567</i>",
        parse_mode="HTML"
    )

@router.message(Form.phone)
async def q_phone(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return
    await state.update_data(phone=message.text.strip())
    await state.set_state(Form.interest)
    await message.answer(
        "<b>6/6</b> — Qaysi yo'nalishga qiziqasiz?\n\n"
        "Quyidagilardan birini tanlang 👇",
        parse_mode="HTML",
        reply_markup=kb.interests_kb()
    )

@router.message(Form.interest)
async def q_interest(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return
    if message.text not in INTERESTS:
        await message.answer("Iltimos, quyidagi tugmalardan birini tanlang! 👇")
        return
    await state.update_data(interest=message.text)
    data = await state.get_data()
    await state.set_state(Form.confirm)
    await message.answer(
        f"📄 <b>Arizangiz:</b>\n\n{preview(data)}\n\n"
        "Tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=kb.confirm_kb()
    )

# ── Tasdiqlash ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "app_confirm")
async def app_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    fish = data["full_name"]

    # .docx generatsiya qilib foydalanuvchiga yuborish
    docx_path = generate(data)

    await call.message.answer(
        "📄 <b>Arizangiz tayyor!</b>\n\n"
        "Quyidagi faylni yuklab oling:\n"
        "1️⃣ Faylni oching\n"
        "2️⃣ Imzolang (yoki chop etib imzolang)\n"
        "3️⃣ Shu chatga qaytarib yuboring\n\n"
        "⬇️ Fayl yuborilmoqda...",
        parse_mode="HTML",
        reply_markup=kb.cancel_kb()
    )
    await call.message.answer_document(
        FSInputFile(docx_path),
        caption=(
            f"📄 <b>{fish}</b> — shaxsiy arizangiz\n\n"
            "✏️ Imzolang va shu chatga yuboring!"
        ),
        parse_mode="HTML"
    )

    os.remove(docx_path)
    await state.set_state(Form.doc_upload)
    await call.answer()


# ── Imzolangan doc qabul qilish ───────────────────────────────────────────────

@router.message(Form.doc_upload)
async def receive_signed_doc(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=kb.main_kb())
        return

    # Faqat .docx qabul qilamiz
    if not message.document:
        await message.answer(
            "⚠️ Iltimos, <b>.docx</b> faylni yuboring!\n\n"
            "Faylni yuklab oling → imzolang → shu chatga yuboring.",
            parse_mode="HTML"
        )
        return

    file_name = message.document.file_name or ""
    if not file_name.lower().endswith(".docx"):
        await message.answer(
            "⚠️ Faqat <b>.docx</b> formatdagi fayl qabul qilinadi!\n"
            "Iltimos, to'g'ri faylni yuboring.",
            parse_mode="HTML"
        )
        return

    data = await state.get_data()
    fish = data["full_name"]

    # DB ga saqlash
    await db.add_applicant(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=fish,
        fakultet=data["fakultet"],
        yonalish=data["yonalish"],
        guruh=data["guruh"],
        phone=data["phone"],
        interest=data["interest"],
    )

    await message.answer(
        "✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        "Suhbat sanasi va vaqti haqida xabar beramiz.\n"
        "Holat: /mystatus",
        parse_mode="HTML",
        reply_markup=kb.main_kb()
    )

    # Adminga ma'lumot + imzolangan fayl
    admin_text = (
        f"🆕 <b>Yangi ariza!</b>\n\n"
        f"👤 {fish}\n"
        f"🏫 {data['fakultet']}\n"
        f"📚 {data['yonalish']}\n"
        f"👥 Guruh: {data['guruh']}\n"
        f"📞 {data['phone']}\n"
        f"🎯 {data['interest']}\n\n"
        f"🆔 <code>{message.from_user.id}</code>"
    )
    for aid in ADMIN_IDS:
        try:
            await message.bot.send_message(aid, admin_text, parse_mode="HTML")
            # Imzolangan faylni yuborish
            await message.bot.send_document(
                aid,
                message.document.file_id,
                caption=f"📄 {fish} — imzolangan ariza fayli"
            )
        except Exception as e:
            log.warning(f"Admin {aid}: {e}")

    await state.clear()

# ── Tahrirlash ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "app_edit")
async def app_edit(call: CallbackQuery):
    await call.message.answer("Qaysi ma'lumotni o'zgartirmoqchisiz?",
                              reply_markup=kb.edit_kb())
    await call.answer()

EDIT_FIELDS = {
    "ed_full_name": ("full_name",  "To'liq ism (F.I.Sh.)"),
    "ed_fakultet":  ("fakultet",   "Fakultet"),
    "ed_yonalish":  ("yonalish",   "Ta'lim yo'nalishi"),
    "ed_guruh":     ("guruh",       "Guruh"),
    "ed_phone":     ("phone",       "Telefon raqam"),
    "ed_interest":  ("interest",   "Qiziqish yo'nalishi"),
}

@router.callback_query(F.data.startswith("ed_") & ~F.data.in_({"ed_back"}))
async def edit_field(call: CallbackQuery, state: FSMContext):
    if call.data not in EDIT_FIELDS:
        return
    field, label = EDIT_FIELDS[call.data]
    await state.update_data(editing=field)
    await state.set_state(Edit.waiting)
    if field == "interest":
        await call.message.answer(
            f"✏️ Yangi <b>{label}</b>ni tanlang:",
            parse_mode="HTML",
            reply_markup=kb.interests_kb()
        )
    else:
        await call.message.answer(
            f"✏️ Yangi <b>{label}</b>ni kiriting:",
            parse_mode="HTML",
            reply_markup=kb.cancel_kb()
        )
    await call.answer()

@router.callback_query(F.data == "ed_back")
async def edit_back(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(Form.confirm)
    await call.message.answer(
        f"📄 <b>Arizangiz:</b>\n\n{preview(data)}\n\nTasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=kb.confirm_kb()
    )
    await call.answer()

@router.message(Edit.waiting)
async def save_edit(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.set_state(Form.confirm)
        data = await state.get_data()
        await message.answer(
            f"📄 <b>Arizangiz:</b>\n\n{preview(data)}\n\nTasdiqlaysizmi?",
            parse_mode="HTML",
            reply_markup=kb.confirm_kb()
        )
        return
    data = await state.get_data()
    field = data.get("editing")
    if field == "interest" and message.text not in INTERESTS:
        await message.answer("Iltimos, tugmalardan birini tanlang! 👇")
        return
    await state.update_data(**{field: message.text.strip()})
    await state.set_state(Form.confirm)
    data = await state.get_data()
    await message.answer(
        f"✅ O'zgartirildi!\n\n📄 <b>Arizangiz:</b>\n\n{preview(data)}\n\nTasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=kb.confirm_kb()
    )

# ── Bekor qilish ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "app_cancel")
async def app_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("❌ Ariza bekor qilindi.", reply_markup=kb.main_kb())
    await call.answer()

# ── Suhbat javoblari ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "iv_yes")
async def iv_yes(call: CallbackQuery):
    u = await db.get_applicant(call.from_user.id)
    name = u["full_name"] if u else call.from_user.first_name
    await db.set_interview_reply(call.from_user.id, "yes")
    for aid in ADMIN_IDS:
        try:
            await call.bot.send_message(
                aid,
                f"✅ <b>{name}</b> suhbatga kelishini tasdiqladi!",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("✅ Javobingiz qabul qilindi! O'z vaqtida keling. 👍")
    await call.answer()

@router.callback_query(F.data == "iv_no")
async def iv_no(call: CallbackQuery):
    u = await db.get_applicant(call.from_user.id)
    name = u["full_name"] if u else call.from_user.first_name
    phone = u["phone"] if u else "—"
    await db.set_interview_reply(call.from_user.id, "no")
    for aid in ADMIN_IDS:
        try:
            await call.bot.send_message(
                aid,
                f"❌ <b>{name}</b> suhbatga kela olmasligini bildirdi.\n"
                f"📞 {phone}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Javobingiz qabul qilindi.")
    await call.answer()
