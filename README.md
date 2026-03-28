# 🐍 ClaudeClaw BANDA

> Мультиагентная команда на Claude Code. Установи за 10 минут — получи 5 AI-агентов в Telegram.

---

## Что это

Готовая команда AI-агентов, каждый со своим характером, специализацией и Telegram-ботом. Работает на [ClaudeClaw](https://github.com/earlyaidopters/claudeclaw) — обёртке вокруг Claude Code CLI.

**Не чат-бот.** Каждый агент запускает настоящий `claude` CLI на твоём Mac/Linux и отправляет результат в Telegram. Все твои файлы, скиллы и инструменты — доступны с телефона.

---

## Команда

| Агент | Роль | Модель | Описание |
|-------|------|--------|----------|
| 🐍 **Начо Варгас** | Координатор | Opus | Главный. Тихий, наблюдательный, делает любую работу |
| 🔥 **Туко Саламанка** | Исполнитель | Haiku | Быстрые задачи: конвертация, скрипты, мелкие фиксы |
| 🎭 **Лало Саламанка** | Маркетолог | Sonnet | Тренды, контент, конкуренты, копирайтинг |
| ☕ **Гейл Беттикер** | Программист | Opus | Код, архитектура, тесты, рефакторинг |
| ⚖️ **Ким Уэксслер** | ОТК / Юрист | Sonnet | Проверка качества, документы, compliance |

**Архитектура по стоимости:**
- Opus — для сложных задач (координация, код)
- Sonnet — для средних (маркетинг, проверки)
- Haiku — для рутины (быстро и дёшево)

---

## Что нужно

| Требование | Где взять |
|------------|-----------|
| Mac или Linux | — |
| Node.js 20+ | [nodejs.org](https://nodejs.org) |
| Claude Code CLI | `npm i -g @anthropic-ai/claude-code` |
| Claude аккаунт | [claude.ai](https://claude.ai) (рекомендуем Max с Opus) |
| Telegram | Любой аккаунт |

---

## Установка за 10 минут

### 1. Создай Telegram-ботов

Открой [@BotFather](https://t.me/botfather) и создай ботов (по одному на агента):

| Агент | Пример username |
|-------|-----------------|
| Начо (главный) | `@MyNachoBot` |
| Туко | `@MyTucoBot` |
| Лало | `@MyLaloBot` |
| Гейл | `@MyGaleBot` |
| Ким | `@MyKimBot` |

Сохрани токены — понадобятся через минуту.

### 2. Клонируй и установи

```bash
git clone https://github.com/ai-operacionka/claudeclaw-BANDA.git
cd claudeclaw-BANDA
npm install
```

### 3. Настрой ключи

```bash
cp .env.example .env
```

Открой `.env` и заполни:
```
TELEGRAM_BOT_TOKEN=твой_токен_Начо
ALLOWED_CHAT_ID=твой_telegram_id
TUCO_BOT_TOKEN=токен_Туко
LALO_BOT_TOKEN=токен_Лало
GALE_BOT_TOKEN=токен_Гейла
KIM_BOT_TOKEN=токен_Ким
```

> Свой Telegram ID: напиши [@userinfobot](https://t.me/userinfobot) в Telegram.

### 4. Залогинься в Claude

```bash
claude login
```

### 5. Запусти

```bash
npm run build
npm start              # запуск Начо (главный)
npm run agent:start tuco   # запуск Туко
npm run agent:start lalo   # запуск Лало
npm run agent:start gale   # запуск Гейла
npm run agent:start kim    # запуск Ким
```

### 6. Проверь

Напиши каждому боту в Telegram. Если отвечают — всё работает.

```bash
npm run status         # проверка здоровья системы
```

---

## Или пусть Claude сам поставит

```bash
git clone https://github.com/ai-operacionka/claudeclaw-BANDA.git
cd claudeclaw-BANDA
claude
```

И скажи:
> Прочитай README.md и .env.example. Помоги мне настроить проект — установи зависимости, помоги заполнить .env, проверь что всё работает.

---

## Структура проекта

```
claudeclaw-BANDA/
├── agents/           # Агенты (характер, роль, скиллы)
│   ├── tuco/         # Туко Саламанка
│   ├── lalo/         # Лало Саламанка
│   ├── gale/         # Гейл Беттикер
│   ├── kim/          # Ким Уэксслер
│   └── _template/    # Шаблон для нового агента
├── skills/           # Скиллы (навыки агентов)
├── scripts/          # Утилиты и скрипты
├── src/              # Исходный код ClaudeClaw
├── store/            # БД и runtime (создаётся автоматически)
├── workspace/        # Рабочая папка агентов
├── .claudeclaw/      # Конфиг и память Начо
├── .env.example      # Шаблон ключей
└── package.json
```

---

## Как добавить своего агента

```bash
npm run agent:create
```

Или вручную: скопируй `agents/_template/`, заполни `agent.yaml` и `CLAUDE.md`.

---

## Общая память (Hive Mind)

Все агенты пишут в общую SQLite базу — видят что сделали другие. Это не просто 5 отдельных ботов, а команда.

---

## Обновление

```bash
git pull
npm install
npm run build
```

---

## FAQ

**Нужен ли API ключ Anthropic?**
Нет. Если у тебя Claude Max — используется твоя подписка через `claude login`.

**Можно ли запустить только Начо без субагентов?**
Да. `npm start` запускает только главного. Остальные — по желанию.

**Что если я на Free плане Claude?**
Работать будет, но сложные задачи (код, мультиагент) лучше на Opus (Max план).

**Работает на Windows?**
Через WSL2 — да.

---

## Лицензия

Проект для подписчиков [AI ОПЕРАЦИОНКА](https://t.me/Sprut_AI). Основан на [ClaudeClaw](https://github.com/earlyaidopters/claudeclaw).

---

_"I'm not like them. I never was." — Начо Варгас_
