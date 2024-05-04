## Description

### DFFSearch

DFFSearch Bot — это обучающий бот для изучения фреймворка Dialogue Flow Framework (DFF). Он предоставляет интерактивные обучающие сессии, возможность задавать вопросы по фреймворку, связываться с менторами и проходить тесты для проверки знаний.

### JointBertService + DSE - intent and slots extraction 
#### Сборка сервиса

- git clone https://github.com/Tanchik24/DFFJointBert.git
- cd DFFJointBert
- python -m venv .venv
- pip install -r requirements.txt
- run main.py

### RAG 
#### Сборка сервиса

```commandline
git clone https://github.com/shanalyb/dffsearch.git
```

```commandline
cd dffsearch
```

```commandline
pyton -m venv .venv
```

```commandline
pip install -r requirements.txt
```

```commandline
docker compose up
```

```commandline
run backend/app.py
```

## Run the bot

```commandline
cd DFFSearch_BOT
```

```commandline
pyton -m venv .venv
```

```commandline
pip install -r requirements.txt
```
- 
```commandline
docker compose up
```

```commandline
run main.py
```

Build the bot:
```commandline
docker-compose build
```
Testing the bot:
```commandline
docker-compose run assistant pytest test.py
```

Running the bot:
```commandline
docker-compose run assistant python run.py
```

Running in background
```commandline
docker-compose up -d
```