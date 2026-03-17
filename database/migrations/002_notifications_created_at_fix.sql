UPDATE notifications
SET created_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL;

UPDATE notifications
SET message = ''
WHERE message IS NULL;

ALTER TABLE notifications
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE notifications
    ALTER COLUMN message SET NOT NULL;
