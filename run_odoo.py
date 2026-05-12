#!/usr/bin/env python3
import os
import sys
import re
from urllib.parse import urlparse

# Default fallback values for Odoo database connection
db_host = "db"
db_port = "5432"
db_user = "odoo"
db_password = "odoo"
db_name = "odoo"

def is_valid(val):
    if not val:
        return False
    val_str = str(val).strip()
    # If the value starts with '$' (e.g. '$PGPORT', '$PGHOST'), it's an unexpanded placeholder
    if val_str.startswith('$') or val_str == 'False' or val_str == '':
        return False
    return True

print("=== Odoo Railway Bootstrapper ===")

# 1. Parse DATABASE_URL if available
db_url = os.environ.get("DATABASE_URL")
if is_valid(db_url):
    print("Parsing database credentials from DATABASE_URL...")
    try:
        parsed = urlparse(db_url)
        if parsed.hostname:
            db_host = parsed.hostname
        if parsed.port:
            db_port = str(parsed.port)
        if parsed.username:
            db_user = parsed.username
        if parsed.password:
            db_password = parsed.password
        if parsed.path:
            db_name = parsed.path.lstrip('/')
    except Exception as e:
        print(f"Warning: Failed to parse DATABASE_URL: {e}", file=sys.stderr)

# 2. Override with specific PG environment variables if they are valid
if is_valid(os.environ.get("PGHOST")):
    db_host = os.environ.get("PGHOST")
if is_valid(os.environ.get("PGUSER")):
    db_user = os.environ.get("PGUSER")
if is_valid(os.environ.get("PGPASSWORD")):
    db_password = os.environ.get("PGPASSWORD")
if is_valid(os.environ.get("PGDATABASE")):
    db_name = os.environ.get("PGDATABASE")

pg_port = os.environ.get("PGPORT")
if is_valid(pg_port) and pg_port.isdigit():
    db_port = pg_port

# 3. Handle standard non-PG environment variables
if is_valid(os.environ.get("HOST")):
    db_host = os.environ.get("HOST")
if is_valid(os.environ.get("USER")):
    db_user = os.environ.get("USER")
if is_valid(os.environ.get("PASSWORD")):
    db_password = os.environ.get("PASSWORD")

# Ensure db_port is strictly a valid integer
if not db_port.isdigit():
    print(f"Warning: Detected invalid db_port '{db_port}'. Forcing fallback to '5432'.")
    db_port = "5432"

# 4. Inject clean values back into environment variables so Odoo's entrypoint reads them
os.environ["HOST"] = db_host
os.environ["PORT"] = db_port
os.environ["USER"] = db_user
os.environ["PASSWORD"] = db_password

print("Clean Environment Configured:")
print(f"  - DB Host: {db_host}")
print(f"  - DB Port: {db_port}")
print(f"  - DB User: {db_user}")
print(f"  - DB Name: {db_name}")
print("=================================")

# 5. Hand over control to official entrypoint
# Pass the database name explicitly to force connection to the correct DB on startup
args = ["/entrypoint.sh", "odoo", "-d", db_name]

# If there are any custom command-line arguments, append them
if len(sys.argv) > 1:
    # Filter out any arguments that look like unexpanded placeholders
    filtered_args = [arg for arg in sys.argv[1:] if not arg.startswith('$')]
    args.extend(filtered_args)

print(f"Executing: {' '.join(args)}", flush=True)
os.execvp(args[0], args)
