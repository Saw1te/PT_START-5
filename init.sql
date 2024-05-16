SELECT 'CREATE DATABASE replacedbname' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replacedbname')\gexec
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'replacerepluser') THEN
        CREATE USER replacerepluser WITH REPLICATION ENCRYPTED PASSWORD 'replacereplpassword'; 
    END IF; 
END $$;

ALTER USER replacepostgresuser WITH PASSWORD 'replacepostgrespassword';

\c replacedbname;
CREATE TABLE IF NOT EXISTS emails(
    emailid INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS phonenum(
    phoneid INT PRIMARY KEY,
    phonenumbers VARCHAR(255) NOT NULL
);
INSERT INTO emails(emailid, email) VALUES(1, 'example1@mail.ru') ON CONFLICT DO NOTHING;
INSERT INTO emails(emailid, email) VALUES(2, 'google@gmail.com') ON CONFLICT DO NOTHING;
INSERT INTO phonenum(phoneid, phonenumbers) VALUES(1, '89775556677') ON CONFLICT DO NOTHING;
INSERT INTO phonenum(phoneid, phonenumbers) VALUES(2, '+7-999-888-77-66') ON CONFLICT DO NOTHING;
