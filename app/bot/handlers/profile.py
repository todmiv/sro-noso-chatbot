import logging
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
    logger = logging.getLogger(__name__)
    logger.info(f"Processing /profile command from user {message.from_user.id}")
    
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        logger.warning(f"User {message.from_user.id} not found")
        await message.answer(
            "❌ Пользователь не найден. Выполните команду /start для регистрации."
        )
        return
    
    logger.debug(f"Current organization for user {message.from_user.id}: '{user.organization_name}'")
    if not user.organization_name:
        logger.debug(f"Organization missing for user {message.from_user.id}, requesting input")
        await state.set_state(ProfileStates.editing_organization)
        await message.answer("🏢 Введите название вашей организации:")
        return
    else:
        logger.debug(f"User {message.from_user.id} already has organization: '{user.organization_name}'")
    
    logger.debug(f"Showing profile for user {message.from_user.id}")
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
    logger = logging.getLogger(__name__)
    if message.text.startswith('/'):
        logger.debug(f"Command received during organization edit: {message.text}")
        await state.clear()
        return
    
    """Сохраняет новое название организации."""
    current_state = await state.get_state()
    logger.debug(f"State: {current_state}, Received text: '{message.text}'")
    
    if not message.text or message.text.strip() == "":
        logger.warning("Empty organization name received")
        await message.answer("❌ Название организации не может быть пустым.")
        return
        
    if message.text.startswith('/'):
        logger.warning(f"Command received instead of organization: {message.text}")
        await message.answer("❌ Пожалуйста, введите название организации, а не команду.")
        return
        
    org_name = message.text.strip()
    
    # Проверяем что это не команда
    if org_name.startswith('/'):
        logger.warning(f"Invalid organization name (command): {org_name}")
        await message.answer("❌ Название организации не может быть командой. Введите корректное название.")
        return
        
    # Проверяем минимальную длину
    if len(org_name) < 3:
        logger.warning(f"Organization name too short: {org_name}")
        await message.answer("❌ Название организации слишком короткое (минимум 3 символа).")
        return
        
    # Проверяем максимальную длину
    if len(org_name) > 200:
        logger.warning(f"Organization name too long: {len(org_name)} chars")
        await message.answer("❌ Название организации слишком длинное (максимум 200 символов).")
        return
    logger.debug(f"Processing organization name: '{org_name}'")
    
    user_service = UserService()
    try:
        logger.debug(f"Attempting to save organization '{org_name}' for user {message.from_user.id}")
        user_before = await user_service.get_user_by_telegram_id(message.from_user.id)
        logger.debug(f"User before update: {user_before.organization_name if user_before else 'None'}")
        
        logger.info(f"Saving organization for user {message.from_user.id}")
        updated_user = await user_service.register_or_update_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            organization_name=org_name
        )
        
        if not updated_user or updated_user.organization_name != org_name:
            logger.error(f"Failed to update organization for user {message.from_user.id}")
            await message.answer("❌ Ошибка при сохранении организации. Попробуйте позже.")
            return
            
        logger.info(f"Successfully updated organization for user {message.from_user.id} to: '{org_name}'")
        await state.clear()
        logger.info(f"State cleared for user {message.from_user.id}")
        
        # Показываем обновленный профиль
        profile_text = (
            f"👤 **Ваш профиль:**\n\n"
            f"**Имя:** {updated_user.first_name or 'Не указано'}\n"
            f"**Фамилия:** {updated_user.last_name or 'Не указано'}\n"
            f"**Username:** @{updated_user.username or 'Не указано'}\n"
            f"**Организация:** `{updated_user.organization_name or 'Не указано'}`\n"
            f"**Статус членства:** {'✅ Член СРО' if updated_user.is_member else '❌ Не является членом'}"
        )
        await message.answer(profile_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error updating organization for user {message.from_user.id}: {str(e)}")
        await message.answer("❌ Произошла ошибка при сохранении. Попробуйте позже.")
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
