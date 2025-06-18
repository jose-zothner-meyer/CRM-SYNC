
import re

def extract_email(sender: str):
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender
