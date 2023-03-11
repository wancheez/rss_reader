import time

PARSER_RESPONSE = {
    "bozo": 0,
    "feed": {
        "title": "Example Feed",
        "link": "https://example.com",
        "description": "An example feed",
        "updated": (2022, 3, 10, 9, 0, 0, 3, 69, 0),
    },
    "entries": [
        {
            "title": "Example Entry 1",
            "link": "https://example.com/1",
            "description": "This is the first example entry",
            "summary": "This is the first example entry",
            "published": (2022, 3, 10, 9, 0, 0, 3, 69, 0),
            "author": "Jane Doe",
            "rights": "free",
        },
        {
            "title": "Example Entry 2",
            "link": "https://example.com/2",
            "description": "This is the second example entry",
            "summary": "This is the second example entry",
            "published": (2022, 3, 10, 9, 0, 0, 3, 69, 0),
            "author": "Bob Smith",
            "rights": "free",
        },
    ],
}
