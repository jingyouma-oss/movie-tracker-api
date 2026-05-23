import json
from urllib import request


BASE_URL = "http://127.0.0.1:8000"


def call(method: str, path: str, data=None):
    body = None
    headers = {}

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(BASE_URL + path, data=body, headers=headers, method=method)
    with request.urlopen(req) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


steps = [
    ("GET /books", call("GET", "/books")),
    (
        "POST /books dune",
        call(
            "POST",
            "/books",
            {
                "title": "Dune",
                "author": "Frank Herbert",
                "status": "read",
                "rating": 5,
            },
        ),
    ),
    (
        "POST /books 1984",
        call(
            "POST",
            "/books",
            {"title": "1984", "author": "George Orwell", "status": "reading"},
        ),
    ),
    (
        "POST /books clean code",
        call(
            "POST",
            "/books",
            {
                "title": "Clean Code",
                "author": "Robert Martin",
                "status": "want_to_read",
            },
        ),
    ),
    ("GET /books", call("GET", "/books")),
    ("GET /books?status=reading", call("GET", "/books?status=reading")),
    ("GET /books/1", call("GET", "/books/1")),
    (
        "PUT /books/2",
        call("PUT", "/books/2", {"status": "read", "rating": 4}),
    ),
    ("GET /books/stats", call("GET", "/books/stats")),
    ("DELETE /books/3", call("DELETE", "/books/3")),
    ("GET /books", call("GET", "/books")),
]

print(json.dumps(steps, indent=2))
