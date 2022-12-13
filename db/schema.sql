DROP DATABASE IF EXISTS `chatapp_new`;
CREATE DATABASE `chatapp_new`;
USE `chatapp_new`;

DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `friends`;

CREATE TABLE `user` (
	`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, 
	`username` varchar(150) NOT NULL UNIQUE, 
	`password` varchar(128) NOT NULL
);

CREATE TABLE `friends` (
	`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `sender_id` bigint NOT NULL,
    `receiver_id` bigint NOT NULL,
    CONSTRAINT `user_requset_fk` 
    FOREIGN KEY(`sender_id`) REFERENCES `user`(`id`) 
			ON DELETE CASCADE,
	CONSTRAINT `user_accept_fk`
		FOREIGN KEY (`receiver_id`) REFERENCES `user`(`id`)
			ON DELETE CASCADE,
            
	`status` BOOL NOT NULL,
    CONSTRAINT not_equal check (`sender_id` <> `receiver_id`),
    CONSTRAINT unique_together UNIQUE index(sender_id, receiver_id)
);

