def test_redacts_ssn(redactor):
    text, entities = redactor.redact("My client's SSN is 536-22-1987, can you check it?")
    assert text == "My client's SSN is <US_SSN>, can you check it?"
    assert entities == ["US_SSN"]


def test_redacts_bank_account_number(redactor):
    text, entities = redactor.redact("Look up account BMT-10293847 for me")
    assert text == "Look up account <ACCOUNT_NUMBER> for me"
    assert entities == ["ACCOUNT_NUMBER"]


def test_redacts_email(redactor):
    text, entities = redactor.redact("Email jane.doe@example.com about the review")
    assert "jane.doe@example.com" not in text
    assert "<EMAIL_ADDRESS>" in text
    assert "EMAIL_ADDRESS" in entities


def test_leaves_clean_text_alone(redactor):
    assert redactor.redact("What is the balance on the portfolio for my client?") == (
        "What is the balance on the portfolio for my client?", [])
