
# blong: I'm sure it exists a way better implementation somewhere inside python.
def display_secret(string: str):
    """Display only part of a secret string"""
    if len(string) > 15:
        index = 5
    elif len(string) > 10:
        index = 3
    elif len(string) > 3:
        index = 1
    else:
        return "***"

    return f"{string[:index]}***{string[-index:]}"
