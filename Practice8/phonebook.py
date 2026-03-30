from connect import get_connection

conn = get_connection()
cur = conn.cursor()

# Call function
cur.execute("SELECT * FROM search_phonebook(%s)", ("Alice",))
results = cur.fetchall()
for row in results:
    print(row)

# Call procedure
cur.execute("CALL upsert_user(%s, %s, %s)", ("Alice", "Lee", "+77001234567"))
conn.commit()

# Insert many users
users_json = '[{"name": "John", "surname": "Doe", "phone": "+77001230000"}]'
cur.execute("CALL upsert_many_users(%s)", (users_json,))
conn.commit()

# Pagination
cur.execute("SELECT * FROM get_users_paginated(%s, %s)", (5, 0))
print(cur.fetchall())

# Delete user
cur.execute("CALL delete_user(%s, %s)", ("John Doe", None))
conn.commit()

cur.close()
conn.close()