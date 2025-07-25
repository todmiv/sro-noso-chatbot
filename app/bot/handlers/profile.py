from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.user_service import UserService
from app.bot.keyboards.inline_keyboards import get_profile_keyboard

router = Router()


class ProfileStates(StatesGroup):
    editing_organization = State()
    editing_contact = State()


@router.message(Command(commands=['profile']))
async def cmd_profile(message: types.Message, state: FSMContext) -> None:
    """Показывает профиль пользователя."""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer(
            "❌ Пользователь не найден. Выполните команду /start для регистрации."
        )
        return
    
    if not user.organization_name:
        await state.set_state(ProfileStates.editing_organization)
        await message.answer("🏢 Введите название вашей организации:")
        return
    
    profile_text = (
        f"👤 **Ваш профиль:**\n\n"
        f"**Имя:** {user.first_name or 'Не указано'}\n"
        f"**Фамилия:** {user.last_name or 'Не указано'}\n"
        f"**Username:** @{user.username or 'Не указано'}\n"
        f"**Организация:** `{user.organization_name or 'Не указано'}`\n"
        f"**Статус членства:** {'✅ Член СРО' if user.is_member else '❌ Не является членом'}\n"
        f"**Дата регистрации:** {user.registration_date.strftime('%d.%m.%Y') if user.registration_date else 'Не указано'}"
    )
    
    keyboard = get_profile_keyboard(user.is_member)
    await message.answer(profile_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(lambda c: c.data == "edit_organization")
async def edit_organization(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начинает редактирование организации."""
    await state.set_state(ProfileStates.editing_organization)
    await callback.message.answer(
        "🏢 Введите название вашей организации:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")]
        ])
    )
    await callback.answer()


@router.message(ProfileStates.editing_organization)
async def save_organization(message: types.Message, state: FSMContext) -> None:
    if message.text.startswith('/'):
        print(f"[save_organization] Command received: {message.text}, clearing state")
        await state.clear()  # Сбрасываем состояние
        return  # Позволяем команде обработаться нормально
    """Сохраняет новое название организации."""
    current_state = await state.get_state()
    print(f"[save_organization] State: {current_state}, Received text: '{message.text}'")
    
    if not message.text or message.text.strip() == "":
        await message.answer("❌ Название организации не может быть пустым.")
        return
        
    if message.text.startswith('/'):
        print(f"[save_organization] Rejected command: {message.text}")
        await message.answer("❌ Пожалуйста, введите название организации, а не команду.")
        return
        
    if len(message.text) > 200:
        await message.answer("❌ Название организации слишком длинное (максимум 200 символов).")
        return
    
    org_name = message.text.strip()
    print(f"[save_organization] Processing organization: '{org_name}'")
    print(f"[save_organization] Processing organization: '{org_name}'")  # Логируем обработанное значение
    
    user_service = UserService()
    await user_service.register_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        organization_name=org_name
    )
    
    print(f"[save_organization] Updated organization to: '{org_name}'")  # Логируем результат
    await message.answer(
        f"📝 Наименование организации изменено на: `{org_name}`",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="profile")]
            ]
        ),
        parse_mode="Markdown"
    )
    await state.clear()


@router.callback_query(lambda c: c.data == "cancel_edit")
async def cancel_edit(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Отменяет редактирование профиля."""
    await state.clear()
    await callback.message.answer("❌ Редактирование отменено.")
    await callback.answer()


@router.callback_query(lambda c: c.data == "refresh_profile")
async def refresh_profile(callback: types.CallbackQuery) -> None:
    """Обновляет информацию профиля."""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.message.answer("❌ Пользователь не найден.")
        return
    
    profile_text = (
        f"👤 **Ваш профиль (обновлено):**\n\n"
        f"**Имя:** {user.first_name or 'Не указано'}\n"
        f"**Фамилия:** {user.last_name or 'Не указано'}\n"
        f"**Username:** @{user.username or 'Не указано'}\n"
        f"**Организация:** `{user.organization_name or 'Не указано'}`\n"
        f"**Статус членства:** {'✅ Член СРО' if user.is_member else '❌ Не является членом'}\n"
        f"**Дата регистрации:** {user.registration_date.strftime('%d.%m.%Y') if user.registration_date else 'Не указано'}"
    )
    
    keyboard = get_profile_keyboard(user.is_member)
    await callback.message.edit_text(profile_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer("🔄 Профиль обновлен")
