import os
from register import register_face
from train import train_faces
from attendance import start_attendance
from auth import admin_login


def menu():
    print("===== FACE ATTENDANCE SYSTEM =====")
    print("1. Start Attendance")
    print("2. Open Dashboard")
    print("3. Register New Person (Admin Only)")
    print("4. Train Faces (Admin Only)")
    print("5. Exit")


while True:
    menu()
    choice = input("\nEnter choice: ").strip()

    if choice == "1":
        start_attendance()

    elif choice == "2":
        os.system("python dashboard.py")

    elif choice == "3":
        if admin_login():
            person_id = input("Enter ID: ").strip()
            name = input("Enter Name: ").strip()
            register_face(person_id, name)

    elif choice == "4":
        if admin_login():
            train_faces()

    elif choice == "5":
        print("✅ Exiting.....")
        break

    else:
        print("❌ Invalid choice. Try again.\n")
