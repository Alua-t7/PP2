import csv
import json
import sys
from datetime import date, datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_CONFIG, CSV_IMPORT_FILE, JSON_EXPORT_FILE, PAGE_SIZE
from connect import get_connection

# ─────────────────────────────────────────────────────────────
#  Utility helpers
# ─────────────────────────────────────────────────────────────

def _prompt(msg: str, allow_empty: bool = False) -> str:
    while True:
        val = input(msg).strip()
        if val or allow_empty:
            return val
        print("  [!] This field cannot be empty.")


def _choose(options: list[str], prompt: str = "Choose: ") -> str:
    """Present a numbered menu and return the chosen string."""
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  [!] Enter a number 1–{len(options)}.")


def _print_contacts(rows) -> None:
    """Pretty-print a list of contact rows (RealDictRow or dict)."""
    if not rows:
        print("  (no contacts found)")
        return
    sep = "─" * 72
    for r in rows:
        print(sep)
        print(f"  Name     : {r['name']}  (@{r['username']})")
        print(f"  Email    : {r.get('email') or '—'}")
        bday = r.get("birthday")
        print(f"  Birthday : {bday if bday else '—'}")
        print(f"  Group    : {r.get('group_name') or '—'}")
        print(f"  Phones   : {r.get('phones') or '—'}")
        print(f"  Added    : {r.get('created_at', '—')}")
    print(sep)


# ─────────────────────────────────────────────────────────────
#  3.1  Schema initialisation
# ─────────────────────────────────────────────────────────────

def init_schema() -> None:
    """Apply schema.sql and procedures.sql to the connected DB."""
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    for fname in ("schema.sql", "procedures.sql"):
        fpath = os.path.join(base, fname)
        if not os.path.exists(fpath):
            print(f"  [!] {fname} not found – skipping.")
            continue
        with open(fpath) as fh:
            sql = fh.read()
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql)
        print(f"  [✓] {fname} applied.")


# ─────────────────────────────────────────────────────────────
#  3.2  Advanced Console Search & Filter
# ─────────────────────────────────────────────────────────────

def _base_contact_query(sort_col: str = "c.name") -> str:
    """
    Core SELECT that joins contacts → groups → phones.
    Caller appends WHERE / ORDER BY / LIMIT / OFFSET as needed.
    """
    allowed = {"c.name", "c.birthday", "c.created_at"}
    if sort_col not in allowed:
        sort_col = "c.name"
    return f"""
        SELECT
            c.id,
            c.name,
            c.username,
            c.email,
            c.birthday,
            g.name           AS group_name,
            c.created_at,
            STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
                             AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones  p ON p.contact_id = c.id
        {{where}}
        GROUP BY c.id, c.name, c.username, c.email,
                 c.birthday, g.name, c.created_at
        ORDER BY {sort_col}
    """


def _sort_choice() -> str:
    print("\n  Sort by:")
    opts = ["name", "birthday", "date added"]
    choice = _choose(opts)
    return {"name": "c.name", "birthday": "c.birthday",
            "date added": "c.created_at"}[choice]


def filter_by_group() -> None:
    """3.2.1 – Show contacts filtered by group."""
    with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name;")
        groups = cur.fetchall()
    if not groups:
        print("  No groups found.")
        return

    print("\n  Select group:")
    names = [g["name"] for g in groups]
    chosen = _choose(names)
    sort_col = _sort_choice()

    sql = _base_contact_query(sort_col).format(
        where="WHERE g.name = %s"
    )
    with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (chosen,))
        rows = cur.fetchall()

    print(f"\n  Contacts in group '{chosen}':")
    _print_contacts(rows)


def search_by_email() -> None:
    """3.2.2 – Partial email match."""
    fragment = _prompt("  Email fragment to search: ")
    sort_col = _sort_choice()

    sql = _base_contact_query(sort_col).format(
        where="WHERE c.email ILIKE %s"
    )
    with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, (f"%{fragment}%",))
        rows = cur.fetchall()

    print(f"\n  Results for email containing '{fragment}':")
    _print_contacts(rows)


def search_extended() -> None:
    """
    3.2 / 3.4.3 – Calls the server-side search_contacts() function,
    which matches name, username, email and all phones.
    """
    query = _prompt("  Search (name / username / email / phone): ")
    with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM search_contacts(%s);", (query,))
        rows = cur.fetchall()

    print(f"\n  Results for '{query}':")
    _print_contacts(rows)


def paginated_browse() -> None:
    """
    3.2.4 – Console pagination loop using next / prev / quit.
    The paginated_query DB function (from Practice 8) handles
    LIMIT/OFFSET; here we drive it from the console.
    """
    sort_col = _sort_choice()
    page = 0

    while True:
        offset = page * PAGE_SIZE
        sql = (
            _base_contact_query(sort_col).format(where="")
            + " LIMIT %s OFFSET %s"
        )
        with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (PAGE_SIZE, offset))
            rows = cur.fetchall()

        print(f"\n  ── Page {page + 1} ──")
        _print_contacts(rows)

        if len(rows) < PAGE_SIZE:
            print("  (end of list)")
            break

        nav = input("  [n]ext / [p]rev / [q]uit: ").strip().lower()
        if nav == "n":
            page += 1
        elif nav == "p":
            page = max(0, page - 1)
        elif nav == "q":
            break


# ─────────────────────────────────────────────────────────────
#  3.3  Import / Export
# ─────────────────────────────────────────────────────────────

# ── JSON helpers ────────────────────────────────────────────

class _DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def export_to_json() -> None:
    """3.3.1 – Write all contacts (+ phones + group) to a JSON file."""
    sql = _base_contact_query("c.name").format(where="")
    with get_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]

    filepath = _prompt(f"  Output file [{JSON_EXPORT_FILE}]: ", allow_empty=True) \
               or JSON_EXPORT_FILE

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, cls=_DateEncoder, indent=2, ensure_ascii=False)

    print(f"  [✓] {len(rows)} contacts exported to '{filepath}'.")


def import_from_json() -> None:
    """
    3.3.2 – Read contacts from JSON and insert into DB.
    On duplicate username: ask skip or overwrite.
    """
    filepath = _prompt(f"  JSON file to import [{JSON_EXPORT_FILE}]: ",
                       allow_empty=True) or JSON_EXPORT_FILE

    try:
        with open(filepath, encoding="utf-8") as fh:
            contacts = json.load(fh)
    except FileNotFoundError:
        print(f"  [!] File '{filepath}' not found.")
        return
    except json.JSONDecodeError as exc:
        print(f"  [!] JSON parse error: {exc}")
        return

    inserted = skipped = overwritten = 0

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for contact in contacts:
                username  = contact.get("username", "").strip()
                name      = contact.get("name", "").strip()
                email     = contact.get("email")
                birthday  = contact.get("birthday")
                group_nm  = contact.get("group_name")
                phones_str = contact.get("phones", "")

                if not username or not name:
                    print(f"  [!] Skipping row with missing name/username: {contact}")
                    skipped += 1
                    continue

                # Check duplicate
                cur.execute("SELECT id FROM contacts WHERE username = %s;",
                            (username,))
                existing = cur.fetchone()

                if existing:
                    print(f"\n  Duplicate: username='{username}' already exists.")
                    action = _choose(["skip", "overwrite"],
                                     "  Action: ").lower()
                    if action == "skip":
                        skipped += 1
                        continue

                # Resolve group
                group_id = None
                if group_nm:
                    cur.execute("SELECT id FROM groups WHERE name = %s;",
                                (group_nm,))
                    g = cur.fetchone()
                    if g:
                        group_id = g["id"]
                    else:
                        cur.execute(
                            "INSERT INTO groups (name) VALUES (%s) RETURNING id;",
                            (group_nm,)
                        )
                        group_id = cur.fetchone()["id"]

                if existing:
                    cur.execute(
                        """UPDATE contacts
                           SET name=%s, email=%s, birthday=%s, group_id=%s
                           WHERE username=%s RETURNING id;""",
                        (name, email, birthday, group_id, username)
                    )
                    contact_id = cur.fetchone()["id"]
                    cur.execute("DELETE FROM phones WHERE contact_id = %s;",
                                (contact_id,))
                    overwritten += 1
                else:
                    cur.execute(
                        """INSERT INTO contacts (name, username, email, birthday, group_id)
                           VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
                        (name, username, email, birthday, group_id)
                    )
                    contact_id = cur.fetchone()["id"]
                    inserted += 1

                # Re-insert phones (stored as "07xxx (mobile), 08xxx (home)")
                if phones_str:
                    for part in phones_str.split(","):
                        part = part.strip()
                        if "(" in part and part.endswith(")"):
                            num, ptype = part.rsplit("(", 1)
                            num   = num.strip()
                            ptype = ptype.rstrip(")").strip()
                        else:
                            num, ptype = part, "mobile"
                        if num:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) "
                                "VALUES (%s, %s, %s);",
                                (contact_id, num, ptype
                                 if ptype in ("home", "work", "mobile") else "mobile")
                            )

    print(f"\n  [✓] Import complete: "
          f"{inserted} inserted, {overwritten} overwritten, {skipped} skipped.")


# ── Extended CSV import ──────────────────────────────────────

def import_from_csv() -> None:
    """
    3.3.3 – Extended CSV importer that handles new fields:
    name, username, phone, phone_type, email, birthday, group.
    Reuses the upsert procedure from Practice 8 for the contact row
    and adds phones via the new add_phone procedure.
    """
    filepath = _prompt(f"  CSV file [{CSV_IMPORT_FILE}]: ",
                       allow_empty=True) or CSV_IMPORT_FILE

    try:
        with open(filepath, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    except FileNotFoundError:
        print(f"  [!] File '{filepath}' not found.")
        return

    required = {"name", "username"}
    if rows and not required.issubset(set(rows[0].keys())):
        print("  [!] CSV must have at least 'name' and 'username' columns.")
        return

    ok = err = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for row in rows:
                name      = row.get("name", "").strip()
                username  = row.get("username", "").strip()
                phone     = row.get("phone", "").strip()
                ptype     = row.get("phone_type", "mobile").strip().lower()
                email     = row.get("email", "").strip() or None
                birthday  = row.get("birthday", "").strip() or None
                group_nm  = row.get("group", "").strip() or None

                if not name or not username:
                    print(f"  [!] Skipping incomplete row: {row}")
                    err += 1
                    continue

                try:
                    # Resolve / create group
                    group_id = None
                    if group_nm:
                        cur.execute(
                            "SELECT id FROM groups WHERE name = %s;", (group_nm,)
                        )
                        g = cur.fetchone()
                        if g:
                            group_id = g[0]
                        else:
                            cur.execute(
                                "INSERT INTO groups (name) VALUES (%s) RETURNING id;",
                                (group_nm,)
                            )
                            group_id = cur.fetchone()[0]

                    # Upsert contact (name, username core + new fields)
                    cur.execute(
                        """INSERT INTO contacts (name, username, email, birthday, group_id)
                           VALUES (%s, %s, %s, %s, %s)
                           ON CONFLICT (username) DO UPDATE
                               SET name     = EXCLUDED.name,
                                   email    = EXCLUDED.email,
                                   birthday = EXCLUDED.birthday,
                                   group_id = EXCLUDED.group_id
                           RETURNING id;""",
                        (name, username, email, birthday, group_id)
                    )
                    contact_id = cur.fetchone()[0]

                    # Add phone via procedure if provided
                    if phone:
                        if ptype not in ("home", "work", "mobile"):
                            ptype = "mobile"
                        cur.execute(
                            "CALL add_phone(%s, %s, %s);",
                            (username, phone, ptype)
                        )

                    ok += 1
                except Exception as exc:  # noqa: BLE001
                    print(f"  [!] Error on row {row}: {exc}")
                    conn.rollback()
                    err += 1
                    continue

    print(f"\n  [✓] CSV import: {ok} imported, {err} errors.")


# ─────────────────────────────────────────────────────────────
#  3.4  Stored Procedure callers
# ─────────────────────────────────────────────────────────────

def call_add_phone() -> None:
    """3.4.1 – Call add_phone(contact, phone, type)."""
    contact = _prompt("  Contact name or username: ")
    phone   = _prompt("  Phone number: ")
    print("  Phone type:")
    ptype   = _choose(["mobile", "home", "work"])

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s);", (contact, phone, ptype))
    print("  [✓] Phone added.")


def call_move_to_group() -> None:
    """3.4.2 – Call move_to_group(contact, group)."""
    contact = _prompt("  Contact name or username: ")

    # Show existing groups and let user type a new one too
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT name FROM groups ORDER BY name;")
        existing = [r[0] for r in cur.fetchall()]

    print("  Existing groups:", ", ".join(existing))
    group = _prompt("  Target group (existing or new): ")

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s);", (contact, group))
    print("  [✓] Contact moved.")


# ─────────────────────────────────────────────────────────────
#  Main menu
# ─────────────────────────────────────────────────────────────

MENU = [
    # (label, function)
    ("Filter contacts by group",           filter_by_group),
    ("Search contacts by email fragment",  search_by_email),
    ("Extended search (name/phone/email)", search_extended),
    ("Browse contacts with pagination",    paginated_browse),
    ("─── Import / Export ───",            None),
    ("Export all contacts to JSON",        export_to_json),
    ("Import contacts from JSON",          import_from_json),
    ("Import contacts from CSV (extended)",import_from_csv),
    ("─── Stored Procedures ───",          None),
    ("Add phone number to contact",        call_add_phone),
    ("Move contact to group",              call_move_to_group),
    ("─── Setup ───",                      None),
    ("Initialise / update DB schema",      init_schema),
    ("Exit",                               None),
]


def main() -> None:
    print("\n" + "═" * 50)
    print("   PhoneBook Extended  –  Practice 9")
    print("═" * 50)

    while True:
        print()
        for i, (label, _) in enumerate(MENU, 1):
            if label.startswith("───"):
                print(f"\n  {label}")
            else:
                print(f"  {i:2}. {label}")

        raw = input("\n  Your choice: ").strip()
        if not raw.isdigit():
            continue
        idx = int(raw) - 1
        if idx < 0 or idx >= len(MENU):
            continue

        label, fn = MENU[idx]
        if label == "Exit":
            print("  Bye!")
            sys.exit(0)
        if fn is None:
            continue

        print()
        try:
            fn()
        except psycopg2.Error as db_err:
            print(f"\n  [DB ERROR] {db_err}")
        except KeyboardInterrupt:
            print("\n  (cancelled)")


if __name__ == "__main__":
    main()