/*
SQLyog Ultimate v10.51 
MySQL - 8.0.29 : Database - club_management_system
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`club_management_system` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `club_management_system`;

/*Table structure for table `club_activity_applications` */

DROP TABLE IF EXISTS `club_activity_applications`;

CREATE TABLE `club_activity_applications` (
  `application_id` int NOT NULL AUTO_INCREMENT,
  `club_id` int NOT NULL,
  `club_name` varchar(255) NOT NULL,
  `activity_name` varchar(255) NOT NULL,
  `venue` varchar(255) DEFAULT NULL,
  `activity_time` varchar(255) DEFAULT NULL,
  `approved` varchar(3) NOT NULL,
  PRIMARY KEY (`application_id`),
  KEY `fk_application_club_id` (`club_id`),
  KEY `fk_application_club_name` (`club_name`),
  CONSTRAINT `fk_application_club_id` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`club_id`),
  CONSTRAINT `fk_application_club_name` FOREIGN KEY (`club_name`) REFERENCES `clubs` (`club_name`),
  CONSTRAINT `club_activity_applications_chk_1` CHECK ((`approved` in (_utf8mb4'是',_utf8mb4'否')))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;

/*Table structure for table `clubs` */

DROP TABLE IF EXISTS `clubs`;

CREATE TABLE `clubs` (
  `club_id` int NOT NULL AUTO_INCREMENT,
  `club_name` varchar(255) NOT NULL,
  `club_advisor` varchar(255) NOT NULL,
  `member_count` int DEFAULT '0',
  PRIMARY KEY (`club_id`),
  UNIQUE KEY `club_name` (`club_name`),
  KEY `fk_club_advisor` (`club_advisor`),
  CONSTRAINT `fk_club_advisor` FOREIGN KEY (`club_advisor`) REFERENCES `user_login` (`user_name`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb3;

/*Table structure for table `students` */

DROP TABLE IF EXISTS `students`;

CREATE TABLE `students` (
  `student_id` varchar(255) NOT NULL,
  `student_class` varchar(255) NOT NULL,
  `student_name` varchar(255) NOT NULL,
  `student_sex` varchar(255) NOT NULL,
  `student_club` varchar(255) NOT NULL,
  PRIMARY KEY (`student_id`),
  KEY `fk_student_club` (`student_club`),
  CONSTRAINT `fk_student_club` FOREIGN KEY (`student_club`) REFERENCES `clubs` (`club_name`),
  CONSTRAINT `students_chk_1` CHECK ((`student_sex` in (_utf8mb4'男',_utf8mb4'女')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

/*Table structure for table `user_login` */

DROP TABLE IF EXISTS `user_login`;

CREATE TABLE `user_login` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `user_account` varchar(255) NOT NULL,
  `user_name` varchar(255) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `power` int NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_account` (`user_account`),
  UNIQUE KEY `user_name` (`user_name`),
  CONSTRAINT `user_login_chk_1` CHECK ((`power` in (1,2)))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb3;

/* Trigger structure for table `clubs` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `check_club_advisor_limit` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `check_club_advisor_limit` BEFORE INSERT ON `clubs` FOR EACH ROW BEGIN
    DECLARE advisor_club_count INT;
    SELECT COUNT(*) INTO advisor_club_count
    FROM clubs
    WHERE club_advisor = NEW.club_advisor;
    
    IF advisor_club_count >= 3 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '一个老师不能同时指导超过三个社团';
    END IF;
END */$$


DELIMITER ;

/* Trigger structure for table `students` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `update_member_count_after_insert_student` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `update_member_count_after_insert_student` AFTER INSERT ON `students` FOR EACH ROW BEGIN
    UPDATE clubs
    SET member_count = member_count + 1
    WHERE club_name = NEW.student_club;
END */$$


DELIMITER ;

/* Trigger structure for table `students` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `update_member_count_after_update_student` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `update_member_count_after_update_student` AFTER UPDATE ON `students` FOR EACH ROW BEGIN
    -- 如果学生的所属社团变更
    IF OLD.student_club != NEW.student_club THEN
        -- 原所属社团人数减1
        UPDATE clubs
        SET member_count = member_count - 1
        WHERE club_name = OLD.student_club;

        -- 新所属社团人数加1
        UPDATE clubs
        SET member_count = member_count + 1
        WHERE club_name = NEW.student_club;
    END IF;
END */$$


DELIMITER ;

/* Trigger structure for table `students` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `update_member_count_after_delete_student` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `update_member_count_after_delete_student` AFTER DELETE ON `students` FOR EACH ROW BEGIN
    UPDATE clubs
    SET member_count = member_count - 1
    WHERE club_name = OLD.student_club;
END */$$


DELIMITER ;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
