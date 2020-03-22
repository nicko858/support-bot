# Bot assistant

This bot can help you in the process of customer support on [vk](https://vk.com/) and [telegram](https://telegram.org/) platforms.  
Look how it works:  

![](https://raw.githubusercontent.com/nicko858/support-bot/gifs/telegram.gif)

![](https://raw.githubusercontent.com/nicko858/support-bot/gifs/vk.gif)

## Prerequisites

### Telegram instructions

- Create telegram-bot using [bot-father](https://telegram.me/BotFather) and remember it's token
- Create telegram-chat(group) and add bot to chat-members
- Get your chat-id using [this manual](https://stackoverflow.com/a/32572159)

### Dialogflow instructions

- Create dialogflow project using [this manual](https://cloud.google.com/dialogflow/docs/quick/setup). If everything is fine, you'll get project id

- Create agent using [this manual](https://cloud.google.com/dialogflow/docs/quick/build-agent) and download it's json credentials

### VK instructions

- Create new [vk-group](https://vk.com/groups?tab=admin)
- Create group token in section `Работа с API` with the following permissions:
  - *управление сообществом*
  - *сообщения сообщества*
- Enable messages send in `Сообщения` - section

## How to deploy local

Python3 should be already installed.

```bash
    git clone https://github.com/nicko858/support-bot
    cd support-bot
    pip install -r requirements.txt
```

- Create file `.env` in the script directory

- Edit your `.env` - file:

  ```bash
     TELEGRAM_BOT_TOKEN=<your bot token>
     LOGGER_CHAT_ID=<your chat id>

     DIALOG_FLOW_ID=<your dialog-flow id>
     GOOGLE_CRED="path to dialog flow agent credentials json in quotes"

     VK_TOKEN=<your vk-group token>
  ```

## How to run local

At first, you need to train your bot, using dialogflow intents. It is a quite simple.  
All you need is a json file with intents body. You can find a demo intents `job_questions` in project folder.  
So let's train bot whith the demo intents:  

```bash
    python3 bot_training.py ./job_questions
```

Now we are ready to start our bots:

```bash
    nohup python3 vk_bot.py &
    nohup python3 telegram_bot.py &
```

## How to deploy on heroku

- Fork current repository
- Make sure, that you have `Procfile` in the repo root and it has this inside:

  ```bash
    bot-tg: python3 telegram_bot.py
    bot-vk: python3 vk_bot.py  
  ```

- Create account on [heroku](https://id.heroku.com) or use existing
- Create new app and connect your github-account
- After successfull github connection, go to `deploy section`
- Choose `Manual deploy` and click `Deploy Branch`(by default -from master)
- After successfull deploy, go to `Settings` and create environment variables in `Config Vars` section:

  ```bash
     TELEGRAM_BOT_TOKEN: <your bot token>
     LOGGER_CHAT_ID: <your chat id>

     DIALOG_FLOW_ID: <your dialog-flow id>
     GOOGLE_CRED: leave this empty!!

     VK_TOKEN: <your vk-group token>
  ```

- Also, you have to create a buildpack for google-credentials using [this manual](https://github.com/gerywahyunugraha/heroku-google-application-credentials-buildpack)

- Go to `Resources` and make sure that you have this in `Free Dynos` - section:

    ```bash
    bot-tg python3 telegram_bot.py
    bot-vk python3 vk_bot.py
    ```

- Run bots by clicking pencil-icon

## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
