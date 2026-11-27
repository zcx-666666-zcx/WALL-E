START TRANSACTION;
CREATE TEMPORARY TABLE migration_guard (id INT PRIMARY KEY);
INSERT INTO migration_guard VALUES (1);
INSERT INTO migration_guard
SELECT 1 WHERE (SELECT COUNT(*) FROM user WHERE id = 2 AND username = 'test') <> 1
    OR EXISTS (SELECT 1 FROM user WHERE id = 3)
    OR EXISTS (SELECT 1 FROM command WHERE user_id = '3')
    OR EXISTS (SELECT 1 FROM contract_machine WHERE user_id = '3')
    OR EXISTS (SELECT 1 FROM contract_user WHERE user_id = 3)
    OR EXISTS (SELECT 1 FROM event WHERE user_id = '3')
    OR EXISTS (SELECT 1 FROM voice_profile WHERE user_id = 3);
UPDATE user SET id = 3 WHERE id = 2 AND username = 'test';
UPDATE command SET user_id = '3' WHERE user_id = '2';
UPDATE contract_machine SET user_id = '3' WHERE user_id = '2';
UPDATE contract_user SET user_id = 3 WHERE user_id = 2;
UPDATE event SET user_id = '3' WHERE user_id = '2';
UPDATE voice_profile SET user_id = 3 WHERE user_id = 2;
COMMIT;
