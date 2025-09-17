from my_imports import *
from bot_handlers import register_handlers

app = FastAPI()

# Change bot initialization to use AsyncTeleBot
bot = async_bot

# register bot handlers
register_handlers(bot)

# --- FastAPI webhook endpoint ---
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update.de_json(data)
    # Traiter l'update en arrière-plan pour répondre 200 OK immédiatement
    asyncio.create_task(bot.process_new_updates([update]))
    return Response(status_code=200, content="OK")

# --- Startup event to set webhook ---
@app.on_event("startup")
async def on_startup():
    # Remove old webhook if any
    await asyncio.sleep(5)
    await bot.remove_webhook()
    # Set new webhook
    # drop_pending_updates=True pour éviter l'accumulation en cas de redémarrage
    await asyncio.sleep(5)
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print("Webhook set to:", WEBHOOK_URL)