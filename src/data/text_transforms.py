import re

def remove_parentheses(text):
    return re.sub(r'\s*\([^)]*\)', '', text)

