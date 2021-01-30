"""
Simple Telegram Bot to reply to Telegram message by providing funny content
about computer science.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Laughybot send you back a joke when you send the commande /joke.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging, requests, os

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip

TOKEN = "1645251736:AAHgYXX2_ivIsj5M48vDz42Kme5gT6KEuco"

PORT = int(os.environ.get("PORT", 5000))

# Enable logging 
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define commands handlers. 
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when bot receive the command /start"""
    update.message.reply_text("Salut toi, je suis laughybot ! \n Si tu veux un peu rigoler, entres la commande /joke et j'irai chercher pour toi du contenu amusant 😂... Tu lis le texte et tu regardes la vidéo à laquelle le texte renvoit\n /help pour savoir comment je fonctionne \n#d@iki, Just code it !")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when bot receive the command /help"""
    update.message.reply_text("Laughybot\n VERSION\n 0.1 \nUSAGE\n /{command} : Entrer une commande parmi celles disponibles\nCOMMADES  \n/joke => recherche une blague sur la toile\n/start => Affiche le message d'accueil\n/help => Affiche l'aide")

def joke(update: Update, context: CallbackContext) -> None: 
    """"Send a message when bot receive the command /joke"""
    response = scrap_joke()
    update.message.reply_text(response["title"])
    try :
        update.message.reply_video(video=open("store/video.webm", 'rb'), supports_streaming=True)
    except Exception as e :
        pass


# Scrap a joke on the wwww 
def scrap_joke() -> tuple:
    URL = "https://lesjoiesducode.fr/random"
    response = {}

    res = requests.get(URL)
    if res.ok :
        soup = BeautifulSoup(res.content, "html.parser")
        title = soup.select_one('h1[class="blog-post-title single-blog-post-title"]').text
        video_url = soup.select_one('source[type="video/webm"]').get("src")
        r = requests.get(video_url, stream = True )

        if r.ok : 
            with open("store/video.webm", "wb") as video_file:
                for chunk in r.iter_content(chunk_size = 1024*1024):
                    if chunk:
                        video_file.write(chunk)
                
            VideoFileClip("store/video.webm").write_gif("store/video.gif")
            response["title"] = title
            response["video"] = video_url
            response["error"] = ""
        else :
            response["error"] = "une erreur s'est produite :("

    else :
        response["error"] = "une erreur s'est produite :("

    return response

def main():
    """Start the bot."""
    
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to registrer handler
    dispatcher = updater.dispatcher 

    # trigger differents command 
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('joke', joke))

    # on non command
    dispatcher.add_handler(MessageHandler(Filters.text and ~Filters.command, help_command))

    # Starting the bot 
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN

    )

    updater.bot.set_webhook("https://still-shore-89901.herokuapp.com/" + TOKEN)

    updater.idle()

if __name__ == "__main__":
    main()
