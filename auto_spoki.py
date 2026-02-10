import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

# Настройки путей
USER_PATH = Path(os.environ['APPDATA']) / "Code/User/workspaceStorage"
LOG_FOLDER = Path("./LOG-Spoki-Noki")

def parse_copilot_session(session_path):
    """Парсит диалог из JSON структуры Copilot 2026"""
    log_content = []
    try:
        # Копируем файл, чтобы не конфликтовать с VS Code
        temp_file = "temp_session_read.json"
        shutil.copy2(session_path, temp_file)
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)

        # Твоя структура: requests -> message -> text / response -> value
        requests = data.get('requests', [])
        for req in requests:
            # Текст пользователя
            user_msg = req.get('message', {}).get('text', '')
            if not user_msg:
                parts = req.get('message', {}).get('parts', [])
                user_msg = " ".join([p.get('text', '') for p in parts if p.get('kind') == 'text'])
            
            # Текст ответа Copilot
            responses = req.get('response', [])
            ai_msg = "\n".join([res['value'] for res in responses if 'value' in res])

            if user_msg or ai_msg:
                log_content.append(f"### 👤 Я:\n{user_msg}\n\n### 🤖 Copilot:\n{ai_msg}\n\n---\n")
        
        return "\n".join(log_content)
    except Exception as e:
        print(f"❌ Ошибка парсинга {session_path.name}: {e}")
        return None

def run_watcher():
    print("🚀 Автоматизация 'Споки Ноки' запущена...")
    print(f"📂 Слежу за чатами в: {USER_PATH}")
    
    last_saved_mtime = 0
    
    while True:
        try:
            # Ищем все файлы чатов
            sessions = list(USER_PATH.glob("**/chatSessions/*.json"))
            if not sessions:
                time.sleep(10)
                continue

            # Берем самый свежий файл
            latest_session = max(sessions, key=lambda p: p.stat().st_mtime)
            current_mtime = latest_session.stat().st_mtime

            # Если файл изменился
            if current_mtime > last_saved_mtime:
                # Быстрая проверка на триггер без полного парсинга
                content_raw = latest_session.read_text(encoding='utf-8').lower()
                
                if "споки ноки" in content_raw:
                    print(f"🚩 Триггер найден в {latest_session.name}! Сохраняю...")
                    chat_log = parse_copilot_session(latest_session)
                    
                    if chat_log:
                        now = datetime.now().strftime("%Y%m%d-%H%M")
                        LOG_FOLDER.mkdir(exist_ok=True)
                        log_file = LOG_FOLDER / f"MD-Spoki-Noki-{now}.md"
                        
                        with open(log_file, 'w', encoding='utf-8') as md:
                            md.write(f"# Лог завершения сессии {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
                            md.write(chat_log)
                        
                        print(f"✅ УСПЕХ: {log_file}")
                        last_saved_mtime = current_mtime # Чтобы не сохранять одно и то же
                else:
                    # Если триггера нет, просто запоминаем время, чтобы не проверять этот файл зря
                    last_saved_mtime = current_mtime

        except Exception as e:
            print(f"⚠️ Ошибка в цикле: {e}")
        
        time.sleep(5) # Проверка каждые 5 секунд

if __name__ == "__main__":
    try:
        run_watcher()
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен.")
