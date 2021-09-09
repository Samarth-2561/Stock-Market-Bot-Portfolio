import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pymongo

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

id = [912813252]
#1280102397

client = pymongo.MongoClient("") #Data Base URL
db = client.test
mydatabase = client['stock_market']

def start(update, context):
    update.message.reply_text('Hey this is a Stock Market Bot!\nFor more Info use \help')

def check_update_time(update, context):
    date_info = list(mydatabase.time_check.find())
    data_text = "The Bot Updates the Information at: "
    for i in date_info[0]['hour']:
      data_text+=str(i)+":00\n"
    update.message.reply_text(data_text)

def modify_time(update, context):
    time_string = update['message']['text'][13::].split(" ")
    old_time = time_string[0].split(':')[0]
    new_time = time_string[1].split(':')[0]
    date_info = list(mydatabase.time_check.find())[0]
    if(int(old_time) in date_info['hour']):
      hour = date_info['hour']
      if(hour.count(int(new_time))):
        update.message.reply_text(
          'Update Time Already Present')
      else:
          hour[hour.index(int(old_time))] = int(new_time)
          minute = date_info['minute']
          payload = {
              'hour': hour,
              'minute': minute
          }
          mydatabase.time_check.delete_many({})
          mydatabase.time_check.insert_one(payload)
          update.message.reply_text(
              'Update Time has been successfully modified from ' + str(old_time) + ':00 to ' + str(new_time)+':00')
    else:
      update.message.reply_text(
        'Invalid Old Time, pls check /check_update_time to get the Update time')

def add_time(update, context):
  time_string = update['message']['text'][9::]
  new_time = time_string.split(":")[0]
  date_info = list(mydatabase.time_check.find())[0]
  hour = date_info['hour']
  if(hour.count(int(new_time))):
    update.message.reply_text(
        'Update Time Already Present')
  else:
      hour.append(int(new_time))
      minute = date_info['minute']
      payload = {
          'hour': hour,
          'minute': minute
      }
      mydatabase.time_check.delete_many({})
      mydatabase.time_check.insert_one(payload)
      update.message.reply_text(
          'Update Time has been successfully Added ' + str(new_time)+':00')

def delete_time(update, context):
  time_string = update['message']['text'][13::]
  delete_time = time_string.split(":")[0]
  date_info = list(mydatabase.time_check.find())[0]
  try:
    hour = date_info['hour']
    minute = date_info['minute']
    hour.remove(int(delete_time))
    payload = {
      'hour': hour,
      'minute': minute
    }
    mydatabase.time_check.delete_many({})
    mydatabase.time_check.insert_one(payload)
    update.message.reply_text(
      'Time Deleted Successfully, Deleted Time: '+str(delete_time)+":00")
  except:
    update.message.reply_text(
      'No Such Update Time Found!')

def check_bot_status(update,context):
    mydatabase.check_bot.update_one({'test':False},{'$set':{'test':True}})

def list_all_superstar(update,context):
    try:
        superstar_info = list(mydatabase.superstars.find({}))
        text = ""
        for i in superstar_info:
            text += "Name: " + i['name'] + '\nurl: ' + i['url'] + '\n\n'
        update.message.reply_text(text)
    except:
        update.message.reply_text("Trouble Connect Database")



def add_superstar(update, context):
    try:
        superstar_info = update['message']['text'][15::].split(",")
        superstar_url = superstar_info[1]
        superstar_name = superstar_info[0]
        collection_name = superstar_name.upper().split(" ")
        mydatabase.superstars.insert_one({
            'name': superstar_name,
            'url': superstar_url,
            'collection_name': "_".join(collection_name)
        })
        update.message.reply_text("The Superstar is successfully Added: "+str(superstar_name))
    except:
        update.message.reply_text("Failed to Add this superstar")

def remove_superstar(update,context):
    if(True):
        try:
            name = update['message']['text'][18::]
            if (len(list(mydatabase.superstars.find({'name': name})))):
                mydatabase.superstars.delete_one({'name': name})
                update.message.reply_text("Superstar: " + name + " Successfully Removed.")
            else:
                update.message.reply_text("Superstar not present in DB")
        except:
            update.message.reply_text("Failed to Remove this superstar")

    else:
        update.message.reply_text("You are not authenticated for this action.")



def help(update, context):
    update.message.reply_text('Functions : \nCheck Update Time -> /check_update_time\nModify Update Time -> /modify_time <old_time> <new_time>\nAdd Update Time -> /add_time <new_time>'
                              '\nDelete Update Time -> /delete_time <time>\nFor Checking the Status of Bot -> /check_status'
                              '\nAdd Superstar /add_superstar <name> , <url>\nFor Checking the list of superstar -> /list_all_superstar\nFor Remove Superstar -> /remove_superstar <name>')

def echo(update, context):
    update.message.reply_text(update.message.text)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    API_Key = '' #API KEY
    updater = Updater(API_Key, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("check_update_time", check_update_time))
    dp.add_handler(CommandHandler("modify_time", modify_time))
    dp.add_handler(CommandHandler("add_time", add_time))
    dp.add_handler(CommandHandler("delete_time", delete_time))
    dp.add_handler(CommandHandler("check_status", check_bot_status))
    dp.add_handler(CommandHandler("add_superstar", add_superstar))
    dp.add_handler(CommandHandler("list_all_superstar", list_all_superstar))
    dp.add_handler(CommandHandler("remove_superstar", remove_superstar))

    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
