# -*- coding: utf-8 -*-
#!/usr/local/bin/python
import json
import telebot
import requests
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from decouple import config

API_TOKEN = config('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)

_logger = telebot.logger

# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'help', 'ajuda'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, u"""\
Olá, sou o bot não oficial to Tesouro Direto
Escreve /taxas para ver as últimas taxas do TD.
Escreve /tudo para ver os últimos preços do TD.
Escreve /DI1F17 /DI1F19 /DI1F20 /DI1F21 /DI1F22 /DI1F25 para ver a cotação dos DI futuro.
Escreve /donate se quiser agradecer ao autor
""")

@bot.message_handler(commands=['tudo'])
def precos(message):
    chat_id = message.chat.id
    data = get_data()
    if data:
        bot.send_message(chat_id, ''.join(data))
    else:
        bot.send_message(chat_id, u'Ocorreu algum erro na consulta dos dados')

@bot.message_handler(commands=['taxas'])
def taxas(message):
    chat_id = message.chat.id
    data = get_data(u'{nom} | C: {txc}% V: {txv}%\n')
    if data:
        bot.send_message(chat_id, ''.join(data))
    else:
        bot.send_message(chat_id, u'Ocorreu algum erro na consulta dos dados')

def get_data(myFormat=None):
    if myFormat is None:
        myFormat = u'{nom} | C: {txc}% / R${puc} | V: {txv}% / R${puv}\n'
    # Get last update data
    url = 'http://tdireto.com/ws/cotacaoPorDiaWS.php?dt=%(day)02d%%2F%(month)02d%%2F%(year)d&dcn=0' % {
        'day': datetime.today().day,
        'month': datetime.today().month,
        'year': datetime.today().year,
    }
    jsjson = requests.get(url)
    content = jsjson.content.decode("utf-8")
    content = json.loads(content)
    if 'data' not in content.keys() or not content['data']:
        date = content.get('dta', False)
        if date:
            url = 'http://tdireto.com/ws/cotacaoPorDiaWS.php?dt=%(day)02d%%2F%(month)02d%%2F%(year)d&dcn=0' % {
                'day': int(date.split(' ')[0].split('/')[0]),
                'month': int(date.split(' ')[0].split('/')[1]),
                'year': int(date.split(' ')[0].split('/')[2]),
            }
            jsjson = requests.get(url)
            content = jsjson.content.decode("utf-8")
            content = json.loads(content)
    if 'data' in content.keys():
        data = content['data']
        last_data = {}
        for row in data:
            if row['tid'] not in last_data.keys():
                last_data[row['tid']] = {}
            if not last_data[row['tid']] or last_data[row['tid']]['dh'] < row['dh']:
                last_data[row['tid']] = row

        response = []
        for tid, row in last_data.items():
            response += [myFormat.format(**row)]
        response = list(sorted(response))
        return response
    else:
        return None

@bot.message_handler(commands=['DI1F17', 'DI1F19', 'DI1F20', 'DI1F21', 'DI1F22', 'DI1F25', 'di1f17', 'di1f19', 'di1f20', 'di1f21', 'di1f22', 'di1f25'])
def send_difut(message):
    _logger.error("message = %s" % (message, ))
    url = 'http://br.advfn.com/bolsa-de-valores/bmf%s/cotacao' % message.text.split('@')[0].upper()
    _logger.error("url = %s" % (url, ))
    content = requests.get(url)
    _logger.error("content = %s" % (content, ))
    soup = BeautifulSoup(content.content)
    difut = soup.findAll('div', attrs={'class': 'TableElement'})[1].findAll('td')[3].text
    if difut:
        chat_id = message.chat.id
        bot.send_message(chat_id, u'%s: %s' % (message.text.split('@')[0].upper(), difut))

@bot.message_handler(commands=['donate'])
def donate(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, u'Aceitamos doações em #bitcoin: 1GBHvQVHsxBzmf4FDsnFwjDrNeozcR8n1a')
    photo = open('/app/jaime_copay_bitcoin_addr.png', 'rb')
    bot.send_photo(chat_id, photo)

bot.polling()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
