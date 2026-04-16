from pathlib import Path

# исходный файл со ссылками (если нужен для контроля)
SRC = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy.md")
# финальный файл, КУДА пишем результат
DST = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\stranicy -ссылки +шифры.md")

# Маппинг ШИФР -> URL (финальный эталон, как ты хочешь видеть)
CODE_TO_URL = {
    "16М30Ф3": "https://tdrusstankosbyt.ru/stanokchpu16303",
    "16А20Ф3": "https://tdrusstankosbyt.ru/stanokchpu1620f3",
    "РТ755Ф3": "https://tdrusstankosbyt.ru/stanokchpu7553",
    "РТ305М": "https://tdrusstankosbyt.ru/stanokchpu305",
    "РТ779Ф3": "https://tdrusstankosbyt.ru/stanokchpu7793",
    "РТ5001": "https://russtankosbyt.tilda.ws/stanokrt5001",
    "РТ5003": "https://russtankosbyt.tilda.ws/stanokrt5003",
    "РТ5004": "https://russtankosbyt.tilda.ws/stanokrt5004",
    "РТ301.01": "https://russtankosbyt.tilda.ws/stanokrtrt301",
    "РТ301.02": "https://russtankosbyt.tilda.ws/stanokrtrt30102",
    "РТ301": "https://russtankosbyt.tilda.ws/stanokrtrt301",
    "РТ917": "https://russtankosbyt.tilda.ws/stanokrtrt917",
    "16К20": "https://russtankosbyt.tilda.ws/stanokrtrt16k20",
    "16К40": "https://russtankosbyt.tilda.ws/stanokrtrt16k40",
    "16Р25": "https://russtankosbyt.tilda.ws/stanokrtrt16p25",
    "1М63Н": "https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300",
    "163": "https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300",
    "ДИП-300": "https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300",
    "ДИП300": "https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300",
    "1Н65": "https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500",
    "165": "https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500",
    "1М65": "https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500",
    "ДИП-500": "https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500",
    "ДИП500": "https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500",
    "РТ117": "https://tdrusstankosbyt.ru/stanokrt117",
    "РТ817": "https://tdrusstankosbyt.ru/stanokrtrt817",
    "1А983": "https://tdrusstankosbyt.ru/stanok1a983",
    "1Н983": "https://tdrusstankosbyt.ru/stanok1h983",
    # сюда же позже добавишь шифры вида Т30101, КЖ1842, 55Ф359.50.000 и т.п.
}

def main():
    # формируем список [ШИФР](URL) в нужном порядке (как в словаре)
    items = [f"[{code}]({url})" for code, url in CODE_TO_URL.items()]

    line = ", ".join(items)

    DST.write_text(line, encoding="utf-8")

    print(f"Сформировано пар шифр→URL: {len(items)}")
    print(f"Результат записан в: {DST}")

if __name__ == "__main__":
    main()