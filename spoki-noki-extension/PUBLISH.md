# Публикация и интеграция расширения Spoki Noki Logger

## Сборка и тестирование
1. Перейдите в папку spoki-noki-extension:
   ```sh
   cd spoki-noki-extension
   npm install
   npm run compile
   ```
2. Откройте эту папку в VS Code и нажмите F5 (Debug Extension) — откроется новое окно VS Code с расширением.
3. В настройках (Ctrl+Shift+P → Preferences: Open Settings (JSON)) добавьте:
   ```json
   "spokiNoki.folder": "chat-logs",
   "spokiNoki.trigger": "споки ноки"
   ```
4. Откройте любой текстовый или markdown-файл, напишите "споки ноки" — лог сохранится автоматически.

## Публикация расширения (опционально)
1. Зарегистрируйтесь на https://marketplace.visualstudio.com/ и установите [vsce](https://code.visualstudio.com/api/working-with-extensions/publishing-extension).
2. В папке расширения:
   ```sh
   vsce package
   vsce publish
   ```

## Создание дополнительных триггеров
- Для запуска по другому триггеру (например, "Добр утро"), добавьте ещё одну настройку в settings.json:
  ```json
  "spokiNoki.trigger": "Добр утро"
  ```
- Можно доработать расширение для поддержки нескольких триггеров (по списку).

---

_Инструкция создана автоматически._
