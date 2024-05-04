import re


class EmailExtractor:
    def extract_emails(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        emails = re.findall(email_pattern, text)
        return emails


email_extractor = EmailExtractor()
