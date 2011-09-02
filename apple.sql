--   mysql --user=blog --password=blog --database=blog < apple.sql
SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(11) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    name VARCHAR(20) NOT NULL,
    avatar VARCHAR(100) NOT NULL,
    token VARCHAR(64) NOT NULL,
    last_time DATETIME DEFAULT '1971-1-1 00:00:00',
    last_longitude DOUBLE DEFAULT 0.0,
    last_latitude DOUBLE DEFAULT 0.0,
    loud_num INT DEFAULT 0,
    distance FLOAT NULL,
    is_admin TINYINT(1) NOT NULL DEFAULT 0,
    block TINYINT(1) NOT NULL DEFAULT 0,
    updated DATETIME,
    created DATETIME
);

DROP TABLE IF EXISTS louds;
CREATE TABLE louds (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    content VARCHAR(70) NOT NULL,
    created DATETIME,
    grade SMALLINT DEFAULT 5,
    block TINYINT(1) NOT NULL DEFAULT 0
    created DATETIME
);

/*
DROP TABLE IF EXISTS apps;
CREATE TABLE APPS (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10) NOT NULL UNIQUE,
    key VARCHAR(11) NOT NULL,
    secret VARCHAR(32) NOT NULL,
    created DATETIME
);

DROP TABLE IF EXISTS vars;
CREATE TABLE vars (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10) NOT NULL UNIQUE,
    value FLOAT NOT NULL
);

*/
