import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export function activate(context: vscode.ExtensionContext) {
  let disposable = vscode.workspace.onDidChangeTextDocument((event) => {
    const config = vscode.workspace.getConfiguration('spokiNoki');
    const trigger = config.get<string>('trigger', 'споки ноки').toLowerCase();
    
    // Проверяем изменения на триггер
    for (const change of event.contentChanges) {
      const insertedText = change.text.toLowerCase();
      if (insertedText.includes(trigger)) {
        saveChatLog(event.document, trigger, config.get<string>('folder', 'chat-logs'));
        break; // Только один раз на изменение
      }
    }
  });

  context.subscriptions.push(disposable);
  vscode.window.showInformationMessage('Spoki Noki Logger активирован!');
}

function saveChatLog(document: vscode.TextDocument, trigger: string, folder: string): void {
  const now = new Date().toISOString().slice(0, 16).replace(/:/g, '').replace('T', '-');
  const filename = path.join(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '', folder, `MD-Spoki-Noki-${now}.md`);
  
  // Создать папку
  const dir = path.dirname(filename);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  // Содержимое: весь текст документа + шапка
  const content = `# Лог беседы (${trigger}) за ${now}\n\n${document.getText()}`;
  
  fs.writeFileSync(filename, content, 'utf-8');
  
  vscode.window.showInformationMessage(`✅ Лог сохранён: ${path.basename(filename)}`);
}
