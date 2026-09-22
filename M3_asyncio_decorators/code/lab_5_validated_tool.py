"""LAB 5 — a decorator WITH arguments: `@validated_tool(rules=...)`.

This is the module's hands-on task, written out in full. The shape is the thing
to learn: a decorator that takes arguments is a *factory* — three functions deep.

    validated_tool(...)  -> returns decorator
    decorator(fn)        -> returns wrapper
    wrapper(*args, ...)  -> validates, then calls fn

Every layer exists for a reason and the lab prints which layer owns which piece
of state.

Run:
    uv run python -m M3_asyncio_decorators.code.lab_5_validated_tool
"""
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable

VALIDATED: list[str] = []


class ToolValidationError(ValueError):
    """Raised when a tool argument does not satisfy its rule."""


def validated_tool(**rules: Callable[[Any], None]):
    """Decorate a tool function so its arguments are checked before it runs.

    Each keyword argument is `parameter_name=<predicate>`. The predicate receives
    the value and must raise `ToolValidationError` (with a message that says what
    IS acceptable) when the value is bad. The predicate is only called when the
    caller actually supplied the value, so defaults are not punished for being
    absent.
    """

    def decorator(fn: Callable) -> Callable:
        signature = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)
            for parameter, predicate in rules.items():
                if parameter not in bound.arguments:
                    continue
                value = bound.arguments[parameter]
                predicate(value)  # raises ToolValidationError when the value is bad
            VALIDATED.append(fn.__name__)
            return fn(*args, **kwargs)

        # Keep the rule set visible for debugging and for a schema generator.
        wrapper.rules = dict(rules)
        return wrapper

    return decorator


def _username(value: str) -> None:
    if not isinstance(value, str):
        raise ToolValidationError(f"username must be a string, got {type(value).__name__}")
    if not 3 <= len(value) <= 32:
        raise ToolValidationError(
            f"username must be 3-32 characters, got {len(value)}: {value!r}"
        )


def _email(value: str) -> None:
    if not isinstance(value, str) or "@" not in value or value.startswith("@"):
        raise ToolValidationError(
            f"email must look like name@host, got {value!r}"
        )


def _age(value: int) -> None:
    if not isinstance(value, int) or value < 18:
        raise ToolValidationError(f"age must be an integer >= 18, got {value!r}")


@validated_tool(username=_username, email=_email, age=_age)
def create_user(username: str, email: str, age: int = 18) -> dict:
    """Create a user account.

    Args:
        username: Unique login name, 3-32 characters.
        email: Must contain '@'.
        age: 18 or older.
    """
    return {"created": username, "email": email, "age": age}


@validated_tool(replicas=lambda n: None if 1 <= n <= 50 else _too_many(n))
def scale_service(name: str, replicas: int = 1) -> dict:
    """Scale a service.

    Args:
        name: Service name.
        replicas: Target replica count, 1-50.
    """
    return {"name": name, "replicas": replicas}


def _too_many(n: int) -> None:
    raise ToolValidationError(f"replicas must be between 1 and 50, got {n}")


def main() -> None:
    print("=== step 1: the good path ===")
    print(f"  {create_user('alice', 'alice@example.com')}")
    print(f"  {create_user('bob', 'bob@example.com', age=42)}")

    print("\n=== step 2: every rule firing ===")
    for call in (
        lambda: create_user("ab", "ab@example.com"),
        lambda: create_user("carol", "carol.example.com"),
        lambda: create_user("dave", "dave@example.com", age=16),
        lambda: scale_service("api", replicas=99),
        lambda: scale_service("api", replicas=3),
    ):
        try:
            print(f"  ok   -> {call()}")
        except ToolValidationError as exc:
            print(f"  bad  -> {type(exc).__name__}: {exc}")

    print("\n=== step 3: metadata survived three layers ===")
    print(f"  __name__         {create_user.__name__}")
    print(f"  __doc__ first    {(inspect.getdoc(create_user) or '').splitlines()[0]}")
    print(f"  __annotations__  {create_user.__annotations__}")
    print(f"  signature        {inspect.signature(create_user)}")
    print(f"  rules attached   {sorted(create_user.rules)}")
    print("  -> functools.wraps ran in the INNER layer; the factory adds nothing on top")

    print("\n=== step 4: the closure chain that makes this work ===")
    print(f"  validated_tool is            {type(validated_tool).__name__}")
    print(f"  validated_tool(...) returns  {type(validated_tool(username=_username)).__name__}")
    print(f"  that returns                 {type(validated_tool(username=_username)(create_user)).__name__}")
    print("  -> three levels: factory -> decorator -> wrapper")

    print("\n=== step 5: what got validated and how often ===")
    print(f"  validated calls: {VALIDATED}")
    print("  -> validation lives in the wrapper; the tool body never sees a bad value")


if __name__ == "__main__":
    main()
