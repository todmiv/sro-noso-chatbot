from aiogram import Router, types
from aiogram.filters import Command

from app.services.user_service import UserService
from app.services.sro_registry_service import SRORegistryService
from app.bot.keyboards.inline_keyboards import get_membership_keyboard

router = Router()


@router.message(Command(commands=['membership']))
async def cmd_membership(message: types.Message) -> None:
    """Показывает информацию о членстве в СРО."""
    print(f"[cmd_membership] Received command from {message.from_user.id}")
    print(f"Raw text: '{message.text}'")
    print(f"Entities: {message.entities}")
    
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer(
            "❌ Пользователь не найден. Выполните команду /start для регистрации."
        )
        return
    
    if user.is_member:
        membership_text = (
            f"✅ **Статус членства в СРО НОСО**\n\n"
            f"**Организация:** {user.organization_name or 'Не указано'}\n"
            f"**Статус:** Действующий член СРО\n"
            f"**Дата вступления:** {user.registration_date.strftime('%d.%m.%Y') if user.registration_date else 'Не указано'}\n\n"
            f"**Доступные услуги:**\n"
            f"• Консультации по документам СРО\n"
            f"• Доступ к внутренним стандартам\n"
            f"• Техническая поддержка\n"
            f"• Уведомления об изменениях"
        )
    else:
        membership_text = (
            "❌ **Вы не являетесь членом СРО НОСО**\n\n"
            "**Для вступления в СРО необходимо:**\n"
            "• Быть юридическим лицом или ИП\n"
            "• Иметь лицензию на строительную деятельность\n"
            "• Соответствовать требованиям по кадровому составу\n"
            "• Внести вступительный взнос\n\n"
            "**Контакты для вступления:**\n"
            "📞 Телефон: +7 (831) 123-45-67\n"
            "📧 Email: info@sronoso.ru\n"
            "🌐 Сайт: https://www.sronoso.ru"
        )
    
    keyboard = get_membership_keyboard(user.is_member)
    await message.answer(membership_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(lambda c: c.data == "check_membership")
async def check_membership_status(callback: types.CallbackQuery) -> None:
    """Проверяет статус членства в реестре СРО."""
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.organization_name:
        await callback.message.answer(
            "❌ Для проверки членства необходимо указать название организации в профиле."
        )
        await callback.answer()
        return
    
    # Показываем процесс проверки
    checking_message = await callback.message.answer("🔍 Проверяем статус в реестре СРО...")
    
    try:
        sro_service = SRORegistryService()
        membership_info = await sro_service.check_membership_status(user.organization_name)
        
        if membership_info:
            result_text = (
                f"✅ **Организация найдена в реестре СРО**\n\n"
                f"**Название:** {membership_info.get('name', 'Не указано')}\n"
                f"**ИНН:** {membership_info.get('inn', 'Не указано')}\n"
                f"**Статус:** {membership_info.get('status', 'Не указано')}\n"
                f"**Дата вступления:** {membership_info.get('join_date', 'Не указано')}\n"
                f"**СРО:** {membership_info.get('sro_name', 'Не указано')}"
            )
        else:
            result_text = (
                "❌ **Организация не найдена в реестре СРО**\n\n"
                "Возможные причины:\n"
                "• Организация не является членом СРО\n"
                "• Неточное название организации\n"
                "• Временные проблемы с реестром\n\n"
                "Для получения точной информации обратитесь в СРО НОСО."
            )
        
        await checking_message.edit_text(result_text, parse_mode="Markdown")
        
    except Exception:
        await checking_message.edit_text(
            "❌ Ошибка при проверке статуса. Попробуйте позже или обратитесь в службу поддержки."
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "membership_benefits")
async def show_membership_benefits(callback: types.CallbackQuery) -> None:
    """Показывает преимущества членства в СРО."""
    benefits_text = (
        "🎯 **Преимущества членства в СРО НОСО:**\n\n"
        "**Правовые преимущества:**\n"
        "• Право на выполнение работ без лицензии\n"
        "• Имущественная ответственность СРО\n"
        "• Защита интересов в госорганах\n\n"
        "**Технические преимущества:**\n"
        "• Доступ к стандартам и регламентам\n"
        "• Консультации по техническим вопросам\n"
        "• Обучение и повышение квалификации\n\n"
        "**Деловые преимущества:**\n"
        "• Участие в тендерах\n"
        "• Деловые контакты\n"
        "• Репутация и доверие заказчиков"
    )
    
    await callback.message.answer(benefits_text, parse_mode="Markdown")
    await callback.answer()
