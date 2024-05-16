SELECT 'CREATE DATABASE replaceDBNAME' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'replaceDBNAME')\gexec
CREATE USER replaceREPLUSER WITH REPLICATION ENCRYPTED PASSWORD 'replaceREPLPASSWORD';
\c replaceDBNAME;
CREATE TABLE emails(
    emailid INT PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);
CREATE TABLE phonenum(
    phoneid INT PRIMARY KEY,
    phonenumbers VARCHAR(255) NOT NULL
);
INSERT INTO emails(emailid, email) VALUES(1, 'example1@mail.ru');
INSERT INTO emails(emailid, email) VALUES(2, 'example2@gmail.com');
INSERT INTO phonenum(phoneid, phonenumbers) VALUES(1, '89998887766');
INSERT INTO phonenum(phoneid, phonenumbers) VALUES(2, '+7-999-555-66-77');

