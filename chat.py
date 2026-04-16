import anthropic

def main():
    client = anthropic.Anthropic(api_key="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")
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Привет, Claude!"}
        ]
    )
    
    print(message.content[0].text)

if __name__ == "__main__":
    main()