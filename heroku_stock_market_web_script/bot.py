import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime
from pytz import timezone
import time

client = pymongo.MongoClient("") #DataBase Link
db = client.test
mydatabase = client['stock_market']

API_Key = '' #API KEY

payload={}
headers = {
  'authority': 'trendlyne.com',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
  'sec-ch-ua-mobile': '?0',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-user': '?1',
  'sec-fetch-dest': 'document',
  'referer': 'https://trendlyne.com/portfolio/bulk-block-deals/53781/rakesh-jhunjhunwala/',
  'accept-language': 'en-US,en;q=0.9',
}

list_name = ['client_name', 'exchange', 'deal_type', 'action','date','avg_price','quantity','percentage_traded']
chat_id = ['-585807019']

base_url = "https://api.telegram.org/bot1791264533:AAF9y6dBQn2xy-BFzcchz9gnTnzKQANjcdo/sendMessage?chat_id=" + str(
  chat_id[0]) + "&text="
error = 0
run = True
bot_started = False

while(run):
    try:
      now_utc = datetime.now(timezone('Asia/Kolkata'))
      test = mydatabase.check_bot.find()
      date_info = list(mydatabase.time_check.find())
      if(list(test)[0]['test']):
          requests.get(base_url + str('Bot is Live'))
          mydatabase.check_bot.delete_many({})
          mydatabase.check_bot.insert_one({'test': False})
      superstars_data = list(mydatabase.superstars.find({}))
    except Exception as e:
        print(str(e))
        requests.get(base_url + str('Bot having trouble connecting to Database(Check Bot Alive Code)'))
        error+=1

    if ((int(now_utc.hour) in date_info[0]['hour']) and (
            date_info[0]['minute'][0] <= int(now_utc.minute) <= date_info[0]['minute'][1])):
      if(bot_started == False):
        requests.get(base_url + str('Bot has Started'))
        bot_started = True
      for superstar in superstars_data:
        index = 0
        count = 0
        headers['referer'] = superstar['url']
        try:
          response = requests.request("GET", superstar['url'], headers=headers, data=payload)
          soup = BeautifulSoup(response.text, 'html.parser')
          stock = soup.find_all(class_='stockrow')
          data = soup.find_all(class_='cen')
          data = data[10:len(data) - 2]
          payload = {
            "stock_name": stock[0]['data-export']
          }
        except Exception as e:
          print(str(e))
          requests.get(base_url + str('Bot having trouble Scraping the Website'))
          error += 1
        for i in data:
          if (count == 8):
            count = 0
            index = index + 1
            try:
              found = list(mydatabase[superstar['collection_name']].find(payload))
              if (len(found) == 0):
                mydatabase[superstar['collection_name']].insert_one(payload)
                text_send = 'Stock Name: ' + str(payload['stock_name']) + '\nClient Name: ' + str(payload[
                  'client_name']) + '\nAction: ' + payload['action'] + '\nDate: ' + payload[
                              'date'] + '\nAverage Price: ' + \
                            payload['avg_price'] + '\nQuantity: ' + payload['quantity']
                if(len(text_send.split('&')) == 0):
                  requests.get(base_url + text_send)
                else:
                  text_send = text_send.replace('&','and')
                  requests.get(base_url + text_send)
                time.sleep(1.5)
            except Exception as e:
              print(str(e))
              requests.get(base_url + str('Bot having trouble connecting to Database(Inserting the Data in DB)'))
              error += 1
            try:
              payload = {
                "stock_name": stock[index]['data-export']
              }
            except:
              pass
          payload[list_name[count]] = i.text.strip()
          count = count + 1
          if (error == 6):
            requests.get(base_url + 'Bot is having some problem Pls Check, Bot is Stopping...')
            run = False
            break
    else:
      if(bot_started):
        requests.get(base_url + 'Scraping Completed')
      error = 0
      bot_started = False