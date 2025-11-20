from pathlib import Path
from cryptography.fernet import Fernet



def _get_fernet(path):
    """
    Reads the key from a specified file and returns it as a Fernet object.

    :param path: The path for the file in the root of the project
    :return: Fernet object
    """
    with open(path / "keyfile.key", "rb") as kf:
        key = kf.read().strip()
        
    return Fernet(key)


def generate_keyfile(path):
    print("\nStart generate keyfile.key...")

    try:
        key = Fernet.generate_key()
        
        with open(path / "keyfile.key", "wb") as f:
            f.write(key)

        print("keyfile.key generated successfully")
    
    except Exception as e:
        print(f"Error generate keyfile.key: {e}")


def generate_password_file(path, password):
    print("\nStart generate password.key...")

    try:
        if not password:
            raise "The password is not set"
        
        key = _get_fernet(path)

        encrypted_password = key.encrypt(password.encode('utf-8'))
        
        with open(path / "password.key", 'wb') as f:
            f.write(encrypted_password)

        print("password.key generated successfully")
    
    except Exception as e:
        print(f"Error generate password.key: {e}")


if __name__ == "__main__":
    base_path = Path(__file__).parent # Defining the path for the files in the root of the project
    password = "1111" # Defining the base password
    
    generate_keyfile(path=base_path) # Generate the keyfile.key
    generate_password_file(path=base_path, password=password) # Generate the password.key
    
    print(f"\nPath to generated files: {base_path}")