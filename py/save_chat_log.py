#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import sys
import argparse

def save_chat_log(chat_text, trigger="споки ноки", folder="chat-logs"):
    if not chat_text or not str(chat_text).strip():
        print("❌ Пустой лог — файл не создаю.")
        return None

    now = datetime.now().strftime("%Y%m%d-%H%M")
    Path(folder).mkdir(exist_ok=True)
    filename = Path(folder) / f"MD-Spoki-Noki-{now}.md"
    
    if filename.exists():
        timestamp = int(datetime.now().timestamp())
        filename = Path(folder) / f"MD-Spoki-Noki-{now}-{timestamp}.md"
    
    content = f"# Лог беседы ({trigger}) за {now}\n\n"
    content += chat_text
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Лог беседы сохранён: {filename}")
    return str(filename)

def main():
    parser = argparse.ArgumentParser(description="Сохранить лог беседы")
    parser.add_argument("chat_file", nargs="?", help="Файл с чатом или stdin")
    parser.add_argument("--trigger", default="споки ноки", help="Триггер")
    parser.add_argument("--folder", default="chat-logs", help="Папка логов")
    args = parser.parse_args()
    
    if args.chat_file:
        with open(args.chat_file, "r", encoding="utf-8") as f:
            chat_text = f.read()
    else:
        chat_text = sys.stdin.read()
    
    save_chat_log(chat_text, args.trigger, args.folder)

if __name__ == "__main__":
    main()
