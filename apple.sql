--   mysql --user=apple --password=apple --database=apple < apple.sql
SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id int(10) unsigned NOT NULL AUTO_INCREMENT,
    phone bigint(20) unsigned NOT NULL UNIQUE,
    password varchar(32) NOT NULL,
    name varchar(20) NOT NULL,
    avatar varchar(100) NULL,
    token varchar(32) NULL,
    last_lat double NOT NULL DEFAULT '0',
    last_lon double NOT NULL DEFAULT '0',
    /*loud_num INT NOT NULL DEFAULT 0,*/
    radius float NULL,
    shadow varchar(2048) NULL,
    is_admin tinyint(1) NOT NULL DEFAULT '0',
    block tinyint(1) NOT NULL DEFAULT '0',
    updated datetime NOT NULL,
    created datetime NOT NULL,
    PRIMARY KEY (id)
);

DROP TABLE IF EXISTS louds;
CREATE TABLE louds (
    id int(10) unsigned NOT NULL AUTO_INCREMENT,
    user_id int(10) unsigned NOT NULL,
    content varchar(70) NOT NULL,
    address varchar(30) NULL,
    lat double NOT NULL,
    lon double NOT NULL,
    grade smallint(2) NOT NULL DEFAULT '5',
    block tinyint(1) NOT NULL DEFAULT '0',
    created datetime NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
