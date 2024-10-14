import re


def clean_text(input_text):
    input_text = input_text.lower()

    # Replace + or - with _
    pattern = r'(?<=\S)[+-](?=\S)'
    replaced_text = re.sub(pattern, '_', input_text)

    return replaced_text