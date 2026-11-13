"""Milestone 4, step 1: hide private details before anything leaves this laptop. Gemini only ever sees placeholders.

    python mask.py        # runs the examples below

We never swap the real values back: Gemini doesn't need them to explain a tax rule.
Money must survive: "KSh 1500000" and "150,000" are the question, so we only mask numbers shaped like an ID.
"""
import re


KRA_PIN = re.compile(r"\b[A-Z]\d{9}[A-Z]\b", re.IGNORECASE)                     # A123456789Z
PHONE = re.compile(r"(?<![\d+])(?:\+?254|0)[\s-]?[17]\d{2}[\s-]?\d{3}[\s-]?\d{3}\b")   # 0712 345 678, +254722000111
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
ID_NUMBER = re.compile(r"(?<![\d,.])\d{7,8}(?![\d,.])")                         # 23456789, but not 23,456,789
MONEY_WORDS = ("ksh", "kshs", "kes", "sh", "shs", "shilingi")


def mask_id_number(match: re.Match)->str:
    """Called for every 7-8 digit number: keep it if the word in front of it means money."""
    text_before = match.string[:match.start()]
    text_before = text_before.lower().rstrip(" .")
    if text_before.endswith(MONEY_WORDS):
        return match.group(0)
    return "<ID_NUMBER>"


def mask(text: str)->str:
    text = KRA_PIN.sub("<KRA_PIN>", text)
    text = EMAIL.sub("<EMAIL>", text)
    text = PHONE.sub("<PHONE>", text)
    text = ID_NUMBER.sub(mask_id_number, text)
    return text




if __name__ == "__main__":
    tests = [
        "My KRA PIN is A123456789Z, how much tax do I owe?",
        "pin yangu ni p051234567q",
        "Nipigie 0712 345 678 ama +254722000111",
        "My ID is 23456789 and my email is brian.o@gmail.com",
        "My salary is KSh 1500000 per year",
        "Nilipata 1,500,000 mwaka huu",
        "I earned Ksh. 25000000 from sales",
        "What does section 12E say about 2025?",
        "My rent is 150000 a month",
        "I sold goods worth 1500000",
    ]
    for test in tests:
        print(f"{test}\n   -> {mask(test)}")