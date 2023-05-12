import logging
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from telegram.ext import Updater, CommandHandler
from mpl_finance import candlestick_ohlc
from datetime import datetime
import matplotlib.dates as mdates
import pandas as pd
import cryptocompare

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Set up the Telegram bot token
TOKEN = '5974634168:AAGu2yk9d00wgmMG-EuTUP4Jf_XlIbYw1dA'

# Create an updater and dispatcher
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

def start(update, context):
    logging.info('start')
    message = "Welcome to the Crypto Candle Chart Bot!\n\n"
    message += "To generate a candlestick chart, use the following command:\n"
    message += "/chart [coin_name] [currency] [days]\n\n"
    message += "Example: /chart BTC USD 30\n"
    message += "This will generate a candlestick chart for Bitcoin (BTC) in USD, covering the last 30 days.\n\n"
    message += "Please enter the command in the correct format to get the desired chart."

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def get_crypto_data(coin_name, currency, days):
    # Make a request to the CryptoCompare API
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={coin_name}&tsym={currency}&limit={days}"
    response = requests.get(url)
    data = response.json()

    # Extract the necessary information from the response
    # Adjust the logic according to the structure of the response from the API
    if 'Data' in data and 'Data' in data['Data']:
        candles = data['Data']['Data']
        # Extract the open, high, low, close data from the candles

        return candles
    else:
        return None

def generate_chart(coin_name, currency, days):
    # Get the candlestick chart data
    candle_data = get_crypto_data(coin_name, currency, days)

    if candle_data is not None:
        # Extract the necessary information from the response
        prices = []
        for candle in candle_data:
            # Extract the timestamp, open, high, low, and close prices from each candle
            timestamp = datetime.fromtimestamp(candle['time'])
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            close_price = candle['close']
            prices.append((timestamp, open_price, high_price, low_price, close_price))

        # Sort the prices based on the timestamp in ascending order
        prices.sort()

        # Create a pandas DataFrame for the table
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(prices, columns=['Date', 'Open', 'High', 'Low', 'Close'])

        # Prepare the data for the candlestick chart
        candlestick_data = [(mdates.date2num(timestamp), open_price, high_price, low_price, close_price) for
                            (timestamp, open_price, high_price, low_price, close_price) in prices]

        # Create the candlestick chart  
        fig, ax = plt.subplots()
        candlestick_ohlc(ax, candlestick_data, width=0.6, colorup='g', colordown='r')

        # Customize the chart
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.set_xlabel('Dates')
        ax.set_ylabel('Currency')
        ax.set_title(f'Candlestick chart for {coin_name} in {currency} ({days})')

        
        # Format y-axis tick labels for specific cases
        if days == '1':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.set_xlabel('Time')
            
        # Format y-axis tick labels without scientific notation
        plt.ticklabel_format(axis='y', style='plain')

        # Save the chart as an image in memory
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)

        return image_stream, df
    else:
        return None, None

def chart(update, context):
    logging.info("Received a message: %s", update.message.text)
    logging.info("entered")
    # Extract the user's inputs from the message
    input_text = update.message.text.split(' ')[1:]  # Remove the command itself (/chart)

    if len(input_text) != 3:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid command! Please use the format: /chart [coin_name] [currency] [days]")
        return

    coin_name, currency, days = input_text

    # Generate the candlestick chart
    chart_image, prices = generate_chart(coin_name, currency, days)

    if chart_image is not None:
        # Send the chart image as a photo in the chat
        context.bot.send_message(chat_id=update.effective_chat.id, text="Here is your requested chart")
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=chart_image)

        if prices is not None:
            # Send the table as a separate message
            # context.bot.send_message(chat_id=update.effective_chat.id, text="Also a table for seeing open, high, low and close values along with dates")
            # data_string = ""
            # for i in range(len(prices)):
            #     data_string += f"DATE and TIME: {prices['Date'][i]}\n"
            #     data_string += f"OPEN: {prices['Open'][i]}\n"
            #     data_string += f"HIGH: {prices['High'][i]}\n"
            #     data_string += f"LOW: {prices['Low'][i]}\n"
            #     data_string += f"CLOSE: {prices['Close'][i]}\n"
            #     data_string += "\n"
            # context.bot.send_message(chat_id=update.effective_chat.id, text=data_string)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Thank You For Using Crypto Candle Chart Generator Bot. Happy to help you!!!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="You can start a new conversation by sending '/start' in chatbox")
            
    else:
        # Handle the case when data is not available
        context.bot.send_message(chat_id=update.effective_chat.id, text="Unable to fetch candlestick chart data.")

chart_handler = CommandHandler('chart', chart)
dispatcher.add_handler(chart_handler)


def main():
    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
