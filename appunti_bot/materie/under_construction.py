from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder per materia non ancora pronta"""
    query = update.callback_query
    await query.answer("🚧 Modulo in costruzione...", show_alert=True)

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
