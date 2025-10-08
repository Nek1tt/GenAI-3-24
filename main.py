"""
Запуск pipeline: принимает --desc (строка или файл) и --model.
Сохраняет JSON-файлы в текущую директорию по умолчанию.
"""

import argparse
import os
import json
from model_interface import get_generator, generate_raw_text
from processor import make_final_description

def save_result(result: dict, index: int, out_dir: str = "."):
    os.makedirs(out_dir, exist_ok=True)
    filename = f"description_{index}.json"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return path

def load_descriptions(src: str):
    if os.path.isfile(src):
        with open(src, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    else:
        return [src.strip()]

def main():
    parser = argparse.ArgumentParser(description="Краткое -> развёрнутое эмоциональное описание (>=40 слов), целые предложения")
    parser.add_argument("--desc", required=True, type=str,
                        help="Короткое описание (строка) или путь к файлу со строками")
    parser.add_argument("--model", required=False, type=str, default="Qwen/Qwen2-1.5B-Instruct",
                        help="Модель для генерации (по умолчанию Qwen/Qwen2-1.5B-Instruct)")
    parser.add_argument("--out", required=False, type=str, default=".",
                        help="Папка для сохранения JSON (по умолчанию текущая папка)")
    args = parser.parse_args()

    descriptions = load_descriptions(args.desc)
    if not descriptions:
        print("Нет описаний для обработки.")
        return

    generator = get_generator(args.model)
    if generator is None:
        print("Не удалось инициализировать генератор. Проверьте модель и окружение.")
        return

    results = []
    for i, short_desc in enumerate(descriptions, start=1):
        print(f"[{i}/{len(descriptions)}] Обрабатываю: {short_desc}")
        try:
            raw = generate_raw_text(generator, short_desc)
            final_text = make_final_description(short_desc, raw)
            result = {
                "short_description": short_desc,
                "description": final_text
            }
            out_path = save_result(result, i, out_dir=args.out)
            print(f"Сохранено: {out_path}")
            results.append(result)
        except Exception as e:
            print(f"Ошибка при обработке '{short_desc}': {e}")

    print(f"Готово. Обработано {len(results)} описаний. JSON сохранены в: {os.path.abspath(args.out)}")

if __name__ == "__main__":
    main()
