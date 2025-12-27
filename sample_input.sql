-- Sample SQL-like queries for testing the compiler
-- Phase 01, 02, 03

## This is a multi-line comment
   that spans multiple lines
##

CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT,
    gpa FLOAT
);

CREATE TABLE Courses (
    course_id INT,
    course_name TEXT,
    credits INT
);

-- Insert some students
INSERT INTO Students VALUES (1, 'Alice', 20, 3.8);
INSERT INTO Students VALUES (2, 'Bob', 21, 3.5);
INSERT INTO Students (id, name, age, gpa) VALUES (3, 'Charlie', 19, 3.9);

-- Select queries
SELECT * FROM Students;
SELECT name, age FROM Students WHERE age > 20;
SELECT id, name FROM Students WHERE age = 20 AND gpa > 3.5;

-- Update query
UPDATE Students SET age = 22 WHERE id = 1;
UPDATE Students SET gpa = 4.0, age = 20 WHERE name = 'Alice';

-- Delete query
DELETE FROM Students WHERE age < 20;
DELETE FROM Students WHERE id = 2 OR gpa < 3.0;

