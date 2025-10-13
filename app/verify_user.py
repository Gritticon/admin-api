from database.db_users import User
from sqlalchemy.orm import Session


def verify_user(user_id: int, token: str, db: Session) -> bool:

    """
    Verify if the user exists and the token is valid.

    Args:
        user_id (int): The ID of the user to verify.
        token (str): The token to verify.
        db (Session): The database session.

    Returns:
        bool: True if the user exists and the token is valid, False otherwise.
    """
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return False

    if user.token != token:
        return False

    return True