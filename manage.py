import threading
import telebot
import requests
import urllib
import subprocess
from wav_work import solve, delete
from predict_emotion import make_predict_emotion
from telebot import types
from Spotter_recognition.predict_spotter import make_predict_spotter
import tensorflow as tf

token = '1614991779:AAHzVpGl1ng7HmNHm95WymAUq8AAEkO-xaE'
bot = telebot.TeleBot('1614991779:AAHzVpGl1ng7HmNHm95WymAUq8AAEkO-xaE')
model_cnn = tf.keras.models.load_model('../saved_models/CNN')
model_crnn = tf.keras.models.load_model('../saved_models/CRNN')
model_at_rnn = tf.keras.models.load_model('../saved_models/AT_RNN')
model_ds_cnn = tf.keras.models.load_model('../saved_models/DS_CNN')

flags_emotion = {
    'model': None,
    'path': 'temp.wav',
    'mean': 'emotion_data_service/mean',
    'std': 'emotion_data_service/std',
    'labels': 'emotion_data_service/labels',
}

flags_spotter = {
    'model': None,
    'mean': None,
    'std': None,
    'labels': 'spotter_data_service/labels',
    'path': 'temp.wav',
    'mfcc': {
        'offset': 0,
        'duration': 1,
        'sample_rate': 44100,
        'n_mfcc': 40,
        'columns': 61
    },
    'shift': 200,
    'frame_lenght': 400,
}

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Okey, let's start")
    keyboard = types.InlineKeyboardMarkup();
    key_CNN = types.InlineKeyboardButton(text='CNN', callback_data='CNN');
    key_CRNN = types.InlineKeyboardButton(text='CRNN', callback_data='CRNN');
    key_ATT_RNN = types.InlineKeyboardButton(text='AT_RNN', callback_data='AT_RNN');
    key_DNN = types.InlineKeyboardButton(text='DNN', callback_data='DNN');
    key_DS_CNN = types.InlineKeyboardButton(text='DS_CNN', callback_data='DS_CNN');
    keyboard.add(key_CNN)
    keyboard.add(key_CRNN)
    keyboard.add(key_ATT_RNN)
    keyboard.add(key_DNN)
    keyboard.add(key_DS_CNN)
    bot.send_message(
        message.from_user.id, 
        text="Pick a model for spotter recognition", 
        reply_markup=keyboard
    )

    
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global flags_spotter
    if call.data == "CNN":
        flags_spotter['model'] = 'CNN'
        flags_spotter['mfcc']['n_mfcc'] = 30
        flags_spotter['std'] = 'spotter_data_service/std_30'
        flags_spotter['mean'] = 'spotter_data_service/mean_30'
        bot.send_message(
            call.message.chat.id, 
            'You pick a CNN model'
        );
        bot.send_message(
            call.message.chat.id, 
            'Here you can read a decription : https://arxiv.org/pdf/1711.07128.pdf'
        )
    elif call.data == "CRNN":
        flags_spotter['model'] = 'CRNN'
        flags_spotter['mfcc']['n_mfcc'] = 30
        flags_spotter['std'] = 'spotter_data_service/std_30'
        flags_spotter['mean'] = 'spotter_data_service/mean_30'
        bot.send_message(
            call.message.chat.id, 
            'You pick a CRNN model'
        );
        bot.send_message(
            call.message.chat.id, 
            'Here you can read a decription : https://arxiv.org/pdf/1711.07128.pdf'
        )
    elif call.data == "AT_RNN":
        flags_spotter['model'] = 'AT_RNN'
        flags_spotter['mfcc']['n_mfcc'] = 40
        flags_spotter['std'] = 'spotter_data_service/std_40'
        flags_spotter['mean'] = 'spotter_data_service/mean_40'
        bot.send_message(
            call.message.chat.id, 
            'You pick a ATT_RNN model'
        );
        bot.send_message(
            call.message.chat.id, 
            'Here you can read a decription : https://arxiv.org/pdf/1808.08929.pdf'
        )
    elif call.data == "DNN":
        flags_spotter['model'] = 'DNN'
        flags_spotter['mfcc']['n_mfcc'] = 40
        flags_spotter['std'] = 'spotter_data_service/std_40'
        flags_spotter['mean'] = 'spotter_data_service/mean_40'
        bot.send_message(
            call.message.chat.id, 
            'You pick a DNN model'
        );
        bot.send_message(
            call.message.chat.id, 
            'Here you can read a decription : https://arxiv.org/pdf/1711.07128.pdf'
        )
    elif call.data == "DS_CNN":
        flags_spotter['model'] = 'DS_CNN'
        flags_spotter['mfcc']['n_mfcc'] = 40
        flags_spotter['std'] = 'spotter_data_service/std_40'
        flags_spotter['mean'] = 'spotter_data_service/mean_40'
        bot.send_message(
            call.message.chat.id, 
            'You pick a DS_CNN model'
        );
        bot.send_message(
            call.message.chat.id, 
            'Here you can read a decription : https://arxiv.org/pdf/1711.07128.pdf'
        )


@bot.message_handler(commands=['end'])
def start_message(message):
    bot.send_message(message.chat.id, 'end')


@bot.message_handler(commands=['model'])
def start_message(message):
    global flags_spotter
    spotter_model = flags_spotter['model']
    bot.send_message(message.chat.id, f'Your model for spotter recognition - {spotter_model}')

@bot.message_handler(content_types=['text'])
def get(message):
    print('get message')
    bot.send_message(message.chat.id, message.text)


@bot.message_handler(content_types=['voice'])
def get_audio(audio):
    file_id = audio.voice.file_id
    url = f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}'
    res = requests.get(url).json()
    temp = bot.get_file(file_id)
    file_path = temp.file_path
    urll = f'https://api.telegram.org/file/bot{token}/{file_path}'
    urllib.request.urlretrieve(urll, filename='1.oga', reporthook=None, data=None)
    average_amplitude = solve()
    bot.send_message(audio.chat.id, f'average_amplitude={average_amplitude}')
    #bot.send_photo(audio.chat.id, photo=open('plot1.png', 'rb'))
    #bot.send_photo(audio.chat.id, photo=open('plot2.png', 'rb'))
    #src_filename = 'plot1.png'
    #process = subprocess.call(['del', src_filename], shell=True)
    #src_filename = 'plot2.png'
    #process = subprocess.call(['del', src_filename], shell=True)
    _, res = make_predict_emotion(flags_emotion)
    gender, emotion = res.split('_')
    bot.send_message(audio.chat.id, f'Your gender - {gender}, your emotion - {emotion}')
    if flags_spotter['model'] == 'CRNN':
        indicator, temp, ans = make_predict_spotter(model_crnn, flags_spotter, 0.95)
    elif flags_spotter['model'] == 'CNN':
        indicator, temp, ans = make_predict_spotter(model_cnn, flags_spotter, 0.95)
    elif flags_spotter['model'] == 'AT_RNN':
        indicator, temp, ans = make_predict_spotter(model_at_rnn, flags_spotter, 0.95)
    elif flags_spotter['model'] == 'DNN':
        indicator, temp, ans = make_predict_spotter(model_dnn, flags_spotter, 0.95)
    elif flags_spotter['model'] == 'DS_CNN':
         indicator, temp, ans = make_predict_spotter(model_ds_cnn, flags_spotter, 0.95)
    if len(ans) == 0:
        bot.send_message(audio.chat.id, "Unfortunatelly model did'n recognize any spotter words")
    else:
        bot.send_message(audio.chat.id, ans)
    delete()


bot.polling()
