from phonebook import *

create_table()

while True:
    print("\n1. Insert (console)")
    print("2. Insert (CSV)")
    print("3. Update")
    print("4. Show all")
    print("5. Delete")
    print("0. Exit")

    choice = input("Choose: ")

    if choice == "1":
        insert_from_console()
    elif choice == "2":
        insert_from_csv()
    elif choice == "3":
        update_user()
    elif choice == "4":
        show_all()
    elif choice == "5":
        delete_user()
    elif choice == "0":
        break