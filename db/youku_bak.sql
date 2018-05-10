
SET foreign_key_checks = 0;

DROP TABLE IF EXISTS userinfo,movie,notice,download_record;

CREATE TABLE userinfo (
	id INT PRIMARY KEY NOT NULL auto_increment,
	`name` VARCHAR (32),
	`password` VARCHAR (64),
	is_vip INT,
	locked INT,
	user_type VARCHAR (32)
) ENGINE = INNODB,charset = 'utf8';


CREATE TABLE movie (
	id INT PRIMARY KEY NOT NULL auto_increment,
	`name` VARCHAR (32),
	`path` VARCHAR (255),
	is_free INT DEFAULT 0,
	is_delete INT DEFAULT 0,
	create_time timestamp default current_timestamp,
	user_id int,
	file_md5 VARCHAR (64)
) charset = 'utf8';
create table notice(
	id int not null primary key auto_increment,
	`name` varchar(64),
	content varchar(255),
	create_time timestamp  default current_timestamp,
	user_id int
)charset = 'utf8';
create table download_record(
	id int not null PRIMARY key auto_increment,
	user_id int,
	movie_id int
)charset = 'utf8';



