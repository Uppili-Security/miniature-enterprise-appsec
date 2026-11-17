from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.utils.html import escape
import pickle
import json
import sqlite3


def create_demo_database():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT
        )
    """)

    connection.executemany(
        "INSERT INTO users (username, role) VALUES (?, ?)",
        [
            ("admin", "Administrator"),
            ("alice", "Regular User"),
            ("bob", "Regular User"),
        ]
    )

    return connection


@require_GET
def sqli_demo(request):
    username = request.GET.get("name", "")

    connection = create_demo_database()

    # Intentionally vulnerable SQL construction.
    query = (
        "SELECT id, username, role FROM users "
        "WHERE username = '" + username + "'"
    )

    try:
        results = connection.execute(query).fetchall()

        return JsonResponse({
            "query": query,
            "results": results
        })

    except sqlite3.Error as error:
        return JsonResponse({
            "error": str(error)
        }, status=400)

    finally:
        connection.close()


@require_GET
def blind_sqli_demo(request):
    user_id = request.GET.get("id", "")

    connection = create_demo_database()

    # Intentionally vulnerable SQL construction.
    query = (
        "SELECT username FROM users WHERE id = " + user_id
    )

    try:
        result = connection.execute(query).fetchone()

        return JsonResponse({
            "exists": result is not None
        })

    except sqlite3.Error:
        return JsonResponse({
            "exists": False
        })

    finally:
        connection.close()

@require_POST
def stored_xss_demo(request):
    try:
        data = json.loads(request.body)
        user_input = data.get("content", "")

        # Demonstration only: simulate storing untrusted content.
        return JsonResponse({
            "message": "Content received",
            "stored_content": user_input
        })

    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@require_GET
def reflected_xss_demo(request):
    user_input = request.GET.get("input", "")

    return JsonResponse({
        "message": "Input received",
        "reflected_content": user_input
    })


@require_GET
def ssrf_demo(request):
    target = request.GET.get("url", "")

    # Intentionally unsafe URL handling for SAST demonstration.
    return JsonResponse({
        "message": "URL received for processing",
        "target": target
    })

@require_GET
def path_traversal_demo(request):
    filename = request.GET.get("name", "")

    # Intentionally unsafe path construction for SAST demonstration.
    file_path = "/app/demo_files/" + filename

    return JsonResponse({
        "message": "File path constructed",
        "path": file_path
    })

@require_POST
def command_injection_demo(request):
    try:
        data = json.loads(request.body)
        filename = data.get("filename", "")

        # Intentionally unsafe command construction for SAST demonstration.
        command = "file " + filename

        return JsonResponse({
            "message": "Command constructed",
            "command": command
        })

    except (json.JSONDecodeError, AttributeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

@require_GET
def deserialization_demo(request):
    demo_object = {"username": "alice", "role": "Regular User"}

    # Intentionally demonstrates unsafe deserialization.
    serialized_data = pickle.dumps(demo_object)
    deserialized_data = pickle.loads(serialized_data)

    return JsonResponse({
        "message": "Object deserialized",
        "data": deserialized_data
    })