
-- PostgreSQL / SQL Cheatsheet

-- 1. Database Basics
CREATE DATABASE mydb;                  -- Create database
-- \c mydb                            -- Connect (psql)
-- \l                                 -- List databases
-- \dt                                -- List tables

-- 2. Table Commands
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE users;                     -- Drop table
DROP TABLE IF EXISTS users, posts;   -- Drop multiple tables
-- \d users                           -- Show table schema

-- 3. Data Types (Common)
-- INTEGER       - Whole numbers
-- SERIAL        - Auto-incrementing INT
-- VARCHAR(n)    - Variable-length string (max n)
-- TEXT          - Unlimited string
-- BOOLEAN       - true/false
-- DATE          - Date only
-- TIMESTAMP     - Date + time
-- NUMERIC       - Fixed-point decimal

-- 4. Inserting & Updating Data
INSERT INTO users (name, email) VALUES ('John', 'john@example.com');
INSERT INTO users (name, email) VALUES 
('Alice', 'alice@x.com'), 
('Bob', 'bob@x.com');

UPDATE users SET name = 'Johnny' WHERE user_id = 1;
DELETE FROM users WHERE name = 'Bob';

-- 5. Querying Data
SELECT * FROM users;
SELECT name, email FROM users;
SELECT * FROM users WHERE name = 'Alice';
SELECT * FROM users WHERE email LIKE '%@x.com';
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users LIMIT 10;

-- 6. Joins
SELECT * FROM posts JOIN users ON posts.user_id = users.user_id;
SELECT * FROM posts LEFT JOIN users ON posts.user_id = users.user_id;

-- 7. Constraints
-- PRIMARY KEY       - Uniquely identifies a row
-- FOREIGN KEY       - Enforces relationship to another table
-- NOT NULL          - Disallows NULLs
-- UNIQUE            - Disallows duplicates
-- DEFAULT value     - Fills in default if none provided

-- 8. Altering Tables
ALTER TABLE users ADD COLUMN age INTEGER;
ALTER TABLE users DROP COLUMN age;
ALTER TABLE users RENAME COLUMN email TO contact_email;

-- 9. Aggregate Functions
SELECT COUNT(*) FROM users;
SELECT AVG(age) FROM users;
SELECT user_id, COUNT(*) FROM posts GROUP BY user_id;

-- 10. Indexing
CREATE INDEX idx_users_name ON users(name);

-- 11. Transactions
BEGIN;
UPDATE users SET name = 'Test' WHERE user_id = 1;
-- COMMIT; or ROLLBACK;

-- 12. Sequences & Autoincrement
CREATE SEQUENCE user_seq;
ALTER TABLE users ALTER COLUMN user_id SET DEFAULT nextval('user_seq');

-- 13. Misc / Utilities
ALTER TABLE old_name RENAME TO new_name;
TRUNCATE TABLE users;
SELECT current_database();
SELECT NOW();
