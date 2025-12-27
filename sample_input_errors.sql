-- Sample input file with various errors for testing error handling

-- Lexical error: invalid character
CREATE TABLE @invalid (id INT);

-- Syntax error: missing FROM
SELECT name WHERE id = 1;

-- Semantic error: table doesn't exist
SELECT * FROM NonExistentTable;

-- Semantic error: column doesn't exist
CREATE TABLE Test (id INT, name TEXT);
SELECT invalid_column FROM Test;

-- Semantic error: type mismatch
INSERT INTO Test VALUES (1, 'Name', 123);
INSERT INTO Test VALUES ('wrong', 2);

-- Semantic error: redeclaration
CREATE TABLE Test (id INT);
CREATE TABLE Test (name TEXT);

-- Unclosed string
INSERT INTO Test VALUES (1, 'Unclosed string

-- Unclosed comment
## This comment is not closed

