def validate_age(
    age: int,
):
    if age >= 18:
        return True
    return False


def validate_email(email: str) -> bool:
    if "@" in email and "." in email:
        return True
    return False
