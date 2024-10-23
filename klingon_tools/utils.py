# klingon_tools/utils.py

def klingon_title_case(text: str) -> str:
    """
    Capitalizes the first letter of the first word and all subsequent words 
    with a length greater than 3 characters. Words shorter than or equal to 3 
    characters (except the first word) remain unchanged. Spaces between words 
    are retained.

    Args:
        text (str): The input string containing words to be capitalized.

    Returns:
        str: A new string with the first word capitalized and words longer than 
        3 characters capitalized at the first letter, while other words remain 
        unchanged.

    Example:
        >>> custom_title_case("this is a sample text")
        'This is a Sample Text'

        >>> custom_title_case("hello world and beyond")
        'Hello World and Beyond'

        >>> custom_title_case("do or do not, there is no try")
        'Do or do not, There is no Try'
    """
    words = text.split()
    result = [
        words[0].capitalize()
    ] + [
        word.capitalize() if len(word) > 3 else word
        for word in words[1:]
    ]
    return ' '.join(result)
