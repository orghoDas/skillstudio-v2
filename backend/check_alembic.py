from sqlalchemy import create_engine, text
import re

# Read DATABASE_URL_SYNC from .env
with open('.env', 'r', encoding='utf-8') as f:
    data = f.read()
match = re.search(r"DATABASE_URL_SYNC\s*=\s*(.*)", data)
if not match:
    print('DATABASE_URL_SYNC not found in .env')
    raise SystemExit(1)
url = match.group(1).strip().strip('\"').strip("'")

engine = create_engine(url)
with engine.connect() as conn:
    try:
        res = conn.execute(text('SELECT version_num FROM alembic_version'))
        rows = res.fetchall()
        if not rows:
            print('no alembic_version rows')
        for r in rows:
            print('alembic_version:', r[0])
    except Exception as e:
        print('error querying alembic_version:', e)
