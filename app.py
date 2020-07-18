import logging #if any kind of error happens, to enable logging
from flask import Flask,request
from telegram.ext import Updater,CommandHandler,MessageHandler, Filters, Dispatcher
from telegram import Bot, Update,ReplyKeyboardMarkup
from utils import get_reply, fetch_news, topics_keyboard

# enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__) #logger object taht can create any king logs

TOKEN="1149006764:AAEOpev5R7GZgScR9TwvBktafEqYW-u_MtU"

app= Flask(__name__)#creating a flask object

@app.route('/')
def index():
    return "Hello!"


@app.route(f'/{TOKEN}', methods=['GET', 'POST'])#the route for the callback url
def webhook():
    """webhook view which receives updates from telegram"""
    # create update object from json-format request data
    update = Update.de_json(request.get_json(), bot)
    # process update
    dp.process_update(update)
    return "ok"

def start(bot, update): #bit and update object
    """callback function for /start handler"""
    author = update.message.from_user.first_name #update has a mesage object from that we get the first_name
    reply = "Hi! {}".format(author)
    bot.send_message(chat_id=update.message.chat_id, text=reply)

def _help(bot, update):#it always take stwo arguments
    """callback function for /help handler"""
    help_txt = "Hey! This is a help text."
    bot.send_message(chat_id=update.message.chat_id, text=help_txt)

def news(bot,update):
    bot.send_message(chat_id=update.message.chat_id,text="Choose a category",
        reply_markup=ReplyKeyboardMarkup(keyboard=topics_keyboard,one_time_keyboard=True))


def reply_text(bot, update):
    """callback function for text message handler"""
    intent, reply = get_reply(update.message.text,update.message.chat_id)
    if intent=="KB_getNews":
        articles=fetch_news(reply)
        for article in articles:
            bot.send_message(chat_id=update.message.chat_id, text=article['link'])
    else:
        bot.send_message(chat_id=update.message.chat_id, text=reply)

def echo_sticker(bot, update):
    """callback function for sticker message handler"""
    reply=update.message.sticker.file_id
    bot.send_sticker(chat_id=update.message.chat_id,sticker=reply)

def error(bot, update):
    """callback function for error handler"""
    logger.error("Update '%s' caused error '%s'", update, update.error)#log that particular error

bot=Bot(TOKEN) 
try:# to prevent flodding, when the a lot of request calls try to call the webhook again and again
    bot.set_webhook('https://kb-news-bot.herokuapp.com/' + TOKEN)
except Exception as e:
    print(e)
dp=Dispatcher(bot,None)
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", _help))
dp.add_handler(CommandHandler("news", news))
dp.add_handler(MessageHandler(Filters.text, reply_text))
dp.add_handler(MessageHandler(Filters.sticker, echo_sticker))
dp.add_error_handler(error)

if __name__=="__main__":
    app.run(port=8443)