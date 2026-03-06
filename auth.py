import getpass

# Change these to your own admin credentials
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "12345"


def admin_login():
    print("\n===== ADMIN LOGIN REQUIRED =====")
    email = input("Enter admin email: ").strip()
    password = getpass.getpass("Enter password: ").strip()

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        print("✅ Login successful.\n")
        return True
    else:
        print("❌ Invalid email or password.\n")
        return False
