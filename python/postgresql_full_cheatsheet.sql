--add foreign key
ALTER TABLE table_name
ADD COLUMN new_column_name

ALTER TABLE table_name
ADD CONSTRAINT fk_constraint_name 
FOREIGN KEY(new_column_name)
REFERENCES table_that_your_are_refering_to(column_name)

--create a table with a foreign key
CREATE TABLE table_name
(
    item_id int PRIMARY KEY,
    product_id REFERENCES products(product_id)
)
-- OR

CREATE TABLE table_name
(
    item_id int PRIMARY KEY,
    product_id int,
    FOREIGN KEY(product_id)
    REFERENCES products(product_id)
)

-- TIMESTAMP
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- PostgreSQL / SQL Complete Cheatsheet

-- SECTION 1: DATABASE BASICS
CREATE DATABASE mydb;                    -- Create a database
DROP DATABASE mydb;                      -- Drop a database
-- \l                                   -- List databases
-- \c mydb                              -- Connect to a database (psql)
-- \dt                                  -- List tables

-- SECTION 2: DATA TYPES
-- INTEGER, SERIAL, BIGINT              -- Numbers
-- NUMERIC(10, 2)                       -- Decimal
-- VARCHAR(n), TEXT                     -- Strings
-- DATE, TIME, TIMESTAMP, TIMESTAMPTZ   -- Date/time
-- BOOLEAN                              -- true/false
-- BYTEA                                -- Binary data
-- UUID                                 -- Universally Unique Identifier

-- SECTION 3: DDL (DATA DEFINITION LANGUAGE)

-- Create table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email TEXT UNIQUE,
    hire_date DATE DEFAULT CURRENT_DATE,
    salary NUMERIC(10,2),
    department_id INT REFERENCES departments(id)
);

-- Alter table
ALTER TABLE employees ADD COLUMN active BOOLEAN DEFAULT true;
ALTER TABLE employees RENAME COLUMN email TO work_email;
ALTER TABLE employees DROP COLUMN salary;

-- Drop table
DROP TABLE employees;
DROP TABLE IF EXISTS employees, departments;

-- Rename table
ALTER TABLE employees RENAME TO staff;

-- Create index
CREATE INDEX idx_employees_name ON employees(name);
DROP INDEX idx_employees_name;

-- SECTION 4: DML (DATA MANIPULATION LANGUAGE)

-- Insert data
INSERT INTO employees (name, work_email, department_id) 
VALUES ('Alice', 'alice@example.com', 1);

-- Insert multiple rows
INSERT INTO departments (name) VALUES 
('HR'), ('IT'), ('Sales');

-- Update data
UPDATE employees SET active = false WHERE id = 3;

-- Delete data
DELETE FROM employees WHERE id = 4;

-- Truncate table
TRUNCATE TABLE employees;

-- SECTION 5: SELECT QUERIES

-- Basic select
SELECT * FROM employees;

-- Select specific columns
SELECT name, hire_date FROM employees;

-- Filtering
SELECT * FROM employees WHERE active = true;

-- Pattern matching
SELECT * FROM employees WHERE work_email LIKE '%@example.com';

-- Sorting
SELECT * FROM employees ORDER BY hire_date DESC;

-- Limiting results
SELECT * FROM employees LIMIT 5 OFFSET 10;

-- Distinct values
SELECT DISTINCT department_id FROM employees;

-- Aggregate functions
SELECT COUNT(*), AVG(salary) FROM employees;

-- Grouping and filtering groups
SELECT department_id, COUNT(*) 
FROM employees 
GROUP BY department_id 
HAVING COUNT(*) > 2;

-- Subqueries
SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);

-- Joins
SELECT e.name, d.name AS department
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- SECTION 6: DCL (DATA CONTROL LANGUAGE)

-- Create user
CREATE USER devuser WITH PASSWORD 'password123';

-- Grant privileges
GRANT SELECT, INSERT ON employees TO devuser;

-- Revoke privileges
REVOKE INSERT ON employees FROM devuser;

-- Create role
CREATE ROLE readonly;

-- Grant role to user
GRANT readonly TO devuser;

-- SECTION 7: TCL (TRANSACTION CONTROL LANGUAGE)

BEGIN;
UPDATE employees SET salary = salary + 1000 WHERE department_id = 2;
DELETE FROM employees WHERE active = false;
COMMIT;

-- Or rollback if something goes wrong
ROLLBACK;

-- Savepoint (partial rollback)
SAVEPOINT before_raise;
UPDATE employees SET salary = salary + 500 WHERE id = 1;
ROLLBACK TO SAVEPOINT before_raise;

-- SECTION 8: VIEWS

-- Create view
CREATE VIEW active_employees AS
SELECT * FROM employees WHERE active = true;

-- Query view
SELECT * FROM active_employees;

-- Drop view
DROP VIEW active_employees;

-- SECTION 9: SEQUENCES

-- Manual sequence
CREATE SEQUENCE emp_seq START WITH 1000 INCREMENT BY 1;
SELECT nextval('emp_seq');

-- Attach to column
ALTER TABLE employees ALTER COLUMN id SET DEFAULT nextval('emp_seq');

-- Set sequence value
SELECT setval('emp_seq', 2000);

-- SECTION 10: MISC / FUNCTIONS

-- Current date/time
SELECT CURRENT_DATE, CURRENT_TIME, NOW();

-- Type casting
SELECT '2024-01-01'::DATE;

-- Null checks
SELECT * FROM employees WHERE salary IS NULL;

-- CASE statements
SELECT name,
  CASE 
    WHEN salary >= 5000 THEN 'High'
    WHEN salary >= 3000 THEN 'Medium'
    ELSE 'Low'
  END AS salary_level
FROM employees;
