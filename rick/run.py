from telegram.ext import ApplicationBuilder
from .config import BOT_TOKEN
from .handlers import (
    start_command, help_command, my_chat_member_handler, authorize_command,
    get_command, info_command, ls_command, tmdb_command, amzn, snxt,
    airtel, zee5, hulu, viki, mmax, aha_cmd, dsnp, apple, bms, iq, hbo, up, uj, wetv,
    nf, host_command, rk, manual_poster_handler
)
from telegram.ext import CommandHandler, MessageHandler, ChatMemberHandler, filters
import logging

logger = logging.getLogger("bot.run")

def register(app):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(ChatMemberHandler(my_chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(CommandHandler("authorize", authorize_command))
    app.add_handler(CommandHandler("get", get_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("ls", ls_command))
    app.add_handler(CommandHandler("tmdb", tmdb_command))

    app.add_handler(CommandHandler("amzn", amzn))
    app.add_handler(CommandHandler("snxt", snxt))
    app.add_handler(CommandHandler("airtel", airtel))
    app.add_handler(CommandHandler("zee5", zee5))
    app.add_handler(CommandHandler("hulu", hulu))
    app.add_handler(CommandHandler("apple", apple))
    app.add_handler(CommandHandler("viki", viki))
    app.add_handler(CommandHandler("mmax", mmax))
    app.add_handler(CommandHandler("aha", aha_cmd))
    app.add_handler(CommandHandler("dsnp", dsnp))
    app.add_handler(CommandHandler("bms", bms))
    app.add_handler(CommandHandler("nf", nf))
    app.add_handler(CommandHandler("iq", iq))
    app.add_handler(CommandHandler("hbo", hbo))
    app.add_handler(CommandHandler("up", up))
    app.add_handler(CommandHandler("uj", uj))
    app.add_handler(CommandHandler("wetv", wetv))
    app.add_handler(CommandHandler("rk", rk))

    app.add_handler(MessageHandler(filters.PHOTO, manual_poster_handler))
    app.add_handler(CommandHandler("host", host_command))

def main():
    if not BOT_TOKEN:
        print("Set BOT_TOKEN in environment (.env) first!")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    register(app)
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()