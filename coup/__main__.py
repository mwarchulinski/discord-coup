import coup

bot = coup.Robot()

if __name__ == '__main__':
    bot.run(bot.config.get('token'))
