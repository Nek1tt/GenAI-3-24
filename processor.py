"""
Минимальная постобработка:
- Гарантирует итоговое описание >= MIN_WORDS (40).
- Не обрывает предложения: если нужно обрезать, делаем это по границе предложений.
- Если текста меньше MIN_WORDS, добавляем полноценные краткие предложения-добавки (эмоционального характера),
  чтобы не нарушать требование целых предложений.
"""
import re

MIN_WORDS = 40
MAX_WORDS = 50

# Небольшие готовые полные предложения для дополнения при необходимости (эмоциональные, нейтрально-поддерживающие)
FILLER_SENTENCES = [
    "Это придаёт сцене тёплую и уютную атмосферу.",
    "Вижу лёгкую ностальгию в этих деталях.",
    "Сцена вызывает мягкое ощущение спокойствия и уюта.",
    "Каждая деталь будто хранит свою историю.",
    "Смотреть на это хочется ещё и ещё, ощущая тепло момента."
]

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def split_into_sentences(text: str):
    """
    Простая разбивка на предложения по .!? с сохранением пунктуации.
    Если нет явных знаков конца предложения — возвращаем весь текст как один элемент.
    """
    text = text.strip()
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return [text]
    return parts

def count_words(text: str) -> int:
    if not text:
        return 0
    tokens = re.findall(r"[а-яА-ЯёЁa-zA-Z0-9]+(?:[-'][а-яА-ЯёЁa-zA-Z0-9]+)?", text)
    return len(tokens)

def join_sentences(sentences):
    return " ".join([s.strip() for s in sentences if s and s.strip()])

def take_sentences_within_limit(sentences, max_words):
    """
    Отбирает последовательность предложений слева направо так, чтобы суммарное количество
    слов не превышало max_words. Если первое предложение само длиннее max_words, вернёт его целиком
    (важнее не обрывать предложение).
    """
    selected = []
    total = 0
    for s in sentences:
        w = count_words(s)
        if total == 0 and w > max_words:
            return [s]
        if total + w > max_words:
            break
        selected.append(s)
        total += w
    return selected

def make_final_description(short_desc: str, raw_model_output: str) -> str:
    """
    Возвращает финальный текст:
    - берет модельный вывод (raw_model_output), нормализует;
    - берет целые предложения; отбирает столько предложений, чтобы не превышать MAX_WORDS
      (не обрывая при этом предложение) и чтобы суммарно было >= MIN_WORDS, по возможности;
    - если удалось собрать < MIN_WORDS, добавляет предложения из FILLER_SENTENCES, пока не будет >= MIN_WORDS.
    - если модельный вывод пуст — использует short_desc и дополняет filler'ами.
    """
    if raw_model_output is None:
        raw_model_output = ""
    raw = normalize_whitespace(raw_model_output)
    if not raw:
        # модель не вернула текст — используем короткое описание как основную часть
        base = normalize_whitespace(short_desc or "")
        if not base:
            base = "Изображение."
        sentences = split_into_sentences(base)
    else:
        sentences = split_into_sentences(raw)

    # Отбираем предложения в пределах MAX_WORDS
    selected = take_sentences_within_limit(sentences, MAX_WORDS)
    current_text = join_sentences(selected).strip()
    current_count = count_words(current_text)

    # Если получилось больше MAX_WORDS (в первом предложении) — допускаем это, но не режем
    # Если получилось 0 (например, модель вернула пустую строку) — используем short_desc as sentence
    if current_count == 0:
        base = normalize_whitespace(short_desc or "")
        if base:
            sentences = split_into_sentences(base)
            selected = take_sentences_within_limit(sentences, MAX_WORDS)
            current_text = join_sentences(selected)
            current_count = count_words(current_text)

    # Теперь, если слов меньше MIN_WORDS — добавляем полные прилагательные-предложения
    filler_idx = 0
    while current_count < MIN_WORDS:
        # Добавляем следующее полное предложение из списка
        add = FILLER_SENTENCES[filler_idx % len(FILLER_SENTENCES)]
        filler_idx += 1
        # Если current_text пуст — просто добавляем add
        if current_text:
            current_text = f"{current_text} {add}"
        else:
            current_text = add
        current_count = count_words(current_text)
        # Защита от бесконечного цикла (маловероятно)
        if filler_idx > 10:
            break

    final = normalize_whitespace(current_text)
    return final

