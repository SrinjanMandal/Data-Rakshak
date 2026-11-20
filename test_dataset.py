
TEST_CASES = [
    {
        "id": "PII_001",
        "text": "My PAN number is ABCDE1234F.",
        "expected_entities": ["IN_PAN"],
    },
    {
        "id": "PII_002",
        "text": "My Aadhaar number is 234567890123.",
        "expected_entities": ["IN_AADHAAR"],
    },
    {
        "id": "PII_003",
        "text": "Contact me at 9876543210.",
        "expected_entities": ["IN_PHONE"],
    },
    {
        "id": "PII_004",
        "text": "My email is test@example.com.",
        "expected_entities": ["EMAIL_ADDRESS"],
    },
    {
        "id": "PII_005",
        "text": "GSTIN: 22AAAAA0000A1Z5.",
        "expected_entities": ["IN_GSTIN"],
    },
    {
        "id": "PII_006",
        "text": "The project deadline is next Monday.",
        "expected_entities": [],
    },
    {
        "id": "PII_007",
        "text": "Rahul works in the Computer Science department.",
        "expected_entities": [],
    },
    {
        "id": "PII_008",
        "text": "Email rahul@example.com or call 9876543210.",
        "expected_entities": ["EMAIL_ADDRESS", "IN_PHONE"],
    },
]