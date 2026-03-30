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

## Память и Hive Mind

Все агенты делят **одну SQLite базу** (`store/claudeclaw.db`). Это не 5 отдельных ботов — это команда с общей памятью.

### Как устроена память

**3 слоя поиска:**
1. **Vector search** — семантический поиск по смыслу (OpenAI embeddings)
2. **FTS5 keyword** — полнотекстовый поиск (fallback если нет API ключа)
3. **High-importance** — недавние важные воспоминания

**Hive Mind** — общая доска действий:
- Каждый агент записывает что сделал (agent_id, action, summary)
- Другие агенты видят историю команды
- Координатор (Начо) видит всё

**Consolidation** — автосжатие:
- Старые воспоминания сжимаются в инсайты
- Память не растёт бесконечно

**Разделение по agent_id:**
- Каждый агент пишет со своим `agent_id`
- При поиске видит и свои, и общие записи
- Никто не перезаписывает чужое

### OpenAI API ключ (для embeddings)

Для полноценной векторной памяти нужен `OPENAI_API_KEY` в `.env`. Без него память работает через keyword search — проще, но менее точно.

Получить: [platform.openai.com](https://platform.openai.com) → API keys. Стоимость: ~$0.02 за 1M токенов (практически бесплатно).

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

## Ссылки

- 📺 YouTube: [@alekseiulianov](https://youtube.com/@alekseiulianov)
- 📱 Telegram канал: [@ai-operacionka](https://t.me/ai_operacionka)
- 💬 Чат AI ОПЕРАЦИОНКА: [Присоединиться](https://t.me/+your_invite_link)
- 🔧 Основа: [ClaudeClaw](https://github.com/earlyaidopters/claudeclaw)

---

_"I'm not like them. I never was." — Начо Варгас_
