from pathlib import Path
from cryptography.fernet import Fernet


def _get_fernet(path: Path) -> Fernet:
    """Load encryption key from keyfile and return Fernet instance.

    Args:
        path: Directory where keyfile.key is stored.

    Returns:
        Fernet: Configured Fernet encryption object.

    Raises:
        FileNotFoundError: If keyfile.key does not exist.
        ValueError: If keyfile content is empty or invalid.
    """
    keyfile_path = path / "keyfile.key"

    # Read key from file
    with open(keyfile_path, "rb") as kf:
        key = kf.read().strip()

    if not key:
        raise ValueError("Keyfile is empty or invalid")

    return Fernet(key)


def generate_keyfile(path: Path) -> None:
    """Generate keyfile.key containing a newly generated cryptographic key.

    Args:
        path: Directory where keyfile.key should be created.
    """
    print("\nStart generate keyfile.key...")

    try:
        # Generate secure random key
        key = Fernet.generate_key()

        # Save to file
        with open(path / "keyfile.key", "wb") as f:
            f.write(key)

        print("keyfile.key generated successfully")

    except Exception as e:
        print(f"Error generate keyfile.key: {e}")


def generate_password_file(path: Path, password: str) -> None:
    """Encrypt password using keyfile.key and save it to password.key.

    Args:
        path: Directory where password.key will be created.
        password: Plain password string to encrypt.

    Raises:
        ValueError: If password is empty.
    """
    print("\nStart generate password.key...")

    try:
        if not password:
            raise ValueError("The password is not set")

        # Load encryption key
        key = _get_fernet(path)

        # Encrypt password
        encrypted_password = key.encrypt(password.encode("utf-8"))

        # Save encrypted value
        with open(path / "password.key", "wb") as f:
            f.write(encrypted_password)

        print("password.key generated successfully")

    except Exception as e:
        print(f"Error generate password.key: {e}")


if __name__ == "__main__":
    # Path where secure files will be generated
    base_path: Path = Path(__file__).parent

    # Default password for initial generation
    password: str = "1111"

    # Generate encryption key file
    generate_keyfile(path=base_path)

    # Generate encrypted password file
    generate_password_file(path=base_path, password=password)

    print(f"\nPath to generated files: {base_path}")