def add_author(text: str, author_name: str) -> str:
    if f"@{author_name}".lower() in text.lower():
        return text

    result = f"{text}\n\n------------\nAuthor: @{author_name}"

    return result
