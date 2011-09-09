--   mysql --user=blog --password=blog --database=blog < apple.sql
SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    phone BIGINT UNSIGNED NOT NULL UNIQUE,
    password VARCHAR(32) NOT NULL,
    name VARCHAR(20) NOT NULL,
    avatar VARCHAR(100) NULL,
    token VARCHAR(64) NULL,
    last_lon DOUBLE NOT NULL DEFAULT 0,
    last_lat DOUBLE NOT NULL DEFAULT 0,
    /*loud_num INT NOT NULL DEFAULT 0,*/
    radius FLOAT NULL,
    is_admin TINYINT(1) NOT NULL DEFAULT 0,
    block TINYINT(1) NOT NULL DEFAULT 0,
    updated DATETIME NOT NULL,
    created DATETIME NOT NULL
);

DROP TABLE IF EXISTS louds;
CREATE TABLE louds (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL REFERENCES users(id),
    content VARCHAR(70) NOT NULL,
    lon DOUBLE NOT NULL,
    lat DOUBLE NOT NULL,
    grade SMALLINT(2) NOT NULL DEFAULT 5,
    block TINYINT(1) NOT NULL DEFAULT 0,
    created DATETIME NOT NULL
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
