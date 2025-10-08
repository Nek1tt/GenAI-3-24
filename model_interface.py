"""
Адаптер к generator.py.
Генерирует эмоциональное, развёрнутое описание (модельный вывод — свободный текст).
Промпт специально просит цельные предложения и минимум 40 слов.
"""
from generator import initialize_generator, chat_prompt, generate_text

def get_generator(model_name: str):
    return initialize_generator(model_name)

def generate_raw_text(generator, short_desc: str) -> str:
    """
    Формирует промпт для генерации эмоционального описания.
    Требование: текст должен быть эмоциональным сам по себе, состоять из цельных предложений,
    быть не короче 40 слов, не обрывать предложения.
    Возвращает сырой текст модели (строку).
    """
    if not short_desc or not isinstance(short_desc, str):
        raise ValueError("short_desc должен быть непустой строкой")

    prompt = (
        f"Дано краткое описание изображения: '{short_desc}'.\n"
        "Задача: напиши развёрнутое эмоциональное описание изображения на русском языке.\n"
        "- Используй цельные, полные предложения (с точками, вопросительными или восклицательными знаками).\n"
        "- Описание должно быть эмоциональным (передать настроение сцены через слова и фразы),\n"
        "- Длина: **не короче 40 слов** (можно больше), при этом не обрывай предложения.\n"
        "- Не добавляй меток типа 'EMOTION' или служебного текста — просто тело описания.\n"
    )

    messages = chat_prompt(prompt)

    max_new_tokens = 400
    do_sample = True
    temperature = 0.7
    top_p = 0.9
    repetition_penalty = 1.2

    raw = generate_text(
        generator,
        messages,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty
    )
    return raw
