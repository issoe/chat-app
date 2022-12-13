use `chatapp_new`;

DELIMITER |
DROP PROCEDURE IF EXISTS `add_friend`|
CREATE PROCEDURE `add_friend`(
	OUT id BIGINT,
	p_sender_id BIGINT,
    p_receiver_id BIGINT
)
BEGIN
	INSERT INTO `friends`(sender_id, receiver_id, status) 
		VALUES (p_sender_id, p_receiver_id, false);
        SET id = last_insert_id();
END |

DELIMITER |
DROP PROCEDURE IF EXISTS `get_friend`|
CREATE PROCEDURE `get_friend`(
	user_id BIGINT,
    friend_id BIGINT
)
BEGIN
    SELECT * FROM `friends` AS F 
		WHERE 
			CASE WHEN F.sender_id=user_id
				THEN F.receiver_id = friend_id
				WHEN F.sender_id=friend_id
                THEN F.receiver_id=user_id
			END
		AND F.`status`=1;
END |

DELIMITER |
DROP PROCEDURE IF EXISTS `accept_friend`|
CREATE PROCEDURE `accept_friend`(
	sender_id BIGINT,
    user_id BIGINT
)
BEGIN
	UPDATE `friends` SET `status`=1 
		WHERE `friends`.sender_id=sender_id 
			AND `friends`.receiver_id=user_id;
END |

DELIMITER |
DROP PROCEDURE IF EXISTS `signup`|
CREATE PROCEDURE `signup`(
	OUT id BIGINT,
	p_username varchar(150),
    p_password varchar(128)
)
BEGIN
	INSERT INTO `user`(id,username, `password`) 
		VALUES (NULL, p_username, sha2(p_password, 0));	
	set id = last_insert_id();
END |

DELIMITER |
DROP PROCEDURE IF EXISTS `get_user` |
CREATE PROCEDURE `get_user` (
	uid BIGINT
)
BEGIN 
	SELECT id, username FROM `user` WHERE `user`.id = uid;
END |

DELIMITER |
DROP PROCEDURE IF EXISTS `get_user_by_username` |
CREATE PROCEDURE `get_user_by_username` (
	username CHAR(128)
)
BEGIN 
	SELECT id, username FROM `user` WHERE `user`.username = username;
END |

DELIMITER |
DROP PROCEDURE IF EXISTS `login`|
CREATE PROCEDURE `login` (
	username varchar(150),
	`password` varchar(128)
)
BEGIN
	DECLARE hashpass varchar(128);
	IF NOT exists(SELECT id, username
			  	  FROM `user` 
			  	  WHERE `user`.username=username)
	THEN SIGNAL SQLSTATE '45000' 
		SET MESSAGE_TEXT = 'No username matched';
	END IF;

	SELECT `user`.`password` INTO hashpass
	FROM `user`
	WHERE `user`.username = username;

	IF sha2(`password`,0) <> hashpass
	THEN SIGNAL SQLSTATE '77777'
		SET MESSAGE_TEXT = 'Wrong password';
	END IF;
    
	SELECT id, username
	FROM `user`
	WHERE `user`.username = username;
END |


DELIMITER |
DROP PROCEDURE IF EXISTS `get_friend_list`|
CREATE PROCEDURE `get_friend_list`(
	user_id BIGINT
	)
BEGIN
	SELECT U.id, U.username  FROM `friends` AS F, `user` as U 
		WHERE 
			CASE WHEN F.sender_id = user_id
					THEN F.receiver_id = U.id
				WHEN F.receiver_id = user_id
					THEN F.sender_id= U.id
			END
			AND F.`status` = 1
		GROUP BY U.id;
END |


DELIMITER |
DROP PROCEDURE IF EXISTS `get_friend_requests`|
CREATE PROCEDURE `get_friend_requests`(
	user_id BIGINT
	)
BEGIN
	SELECT U.id, U.username FROM `friends` AS F, `user` as U
		WHERE 
			F.receiver_id = user_id
            AND F.sender_id = U.id
			AND F.`status` = 0
		GROUP BY U.id;
		
END |
