cat > schema.sql <<'EOF'
-- books table
CREATE TABLE IF NOT EXISTS books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  serial_no TEXT UNIQUE,
  type TEXT NOT NULL DEFAULT 'book',
  available INTEGER NOT NULL DEFAULT 1
);

-- users table
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);

-- memberships
CREATE TABLE IF NOT EXISTS memberships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  membership_no TEXT UNIQUE NOT NULL,
  user_id INTEGER NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  duration_months INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- issues (book issues)
CREATE TABLE IF NOT EXISTS issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  book_id INTEGER NOT NULL,
  issue_date TEXT NOT NULL,
  return_date TEXT NOT NULL,
  actual_return_date TEXT,
  fine_paid INTEGER DEFAULT 0,
  fine_amount REAL DEFAULT 0,
  remarks TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(book_id) REFERENCES books(id)
);

-- seed admin user (username: admin, password: admin123)
INSERT OR IGNORE INTO users (username, password, name, role) VALUES ('admin','admin123','Administrator','admin');
-- seed normal user (username: user1, password: user123)
INSERT OR IGNORE INTO users (username, password, name, role) VALUES ('user1','user123','Normal User','user');
EOF

