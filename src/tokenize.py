
def tokenize(text_string, method=None):

    if method is None:
        token_list = text_string.split()
    else:
        raise Exception(f"Tokenization method {method} not recognized")

    return token_list