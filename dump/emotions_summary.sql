-- MySQL dump 10.13  Distrib 8.0.32, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: emotions
-- ------------------------------------------------------
-- Server version	8.0.35-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `summary`
--

DROP TABLE IF EXISTS `summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `summary` (
  `date` date DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `room_number` int NOT NULL,
  `session_id` int NOT NULL,
  `course_name` varchar(100) NOT NULL,
  `completed` tinyint(1) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `total` int NOT NULL,
  `present` int NOT NULL,
  `absent` int NOT NULL,
  `ratio` int NOT NULL,
  `anger` int DEFAULT NULL,
  `disgust` int DEFAULT NULL,
  `fear` int DEFAULT NULL,
  `happy` int DEFAULT NULL,
  `neutral` int DEFAULT NULL,
  `sad` int DEFAULT NULL,
  `surprise` int DEFAULT NULL,
  `unknown` int DEFAULT NULL,
  `late_students` int DEFAULT NULL,
  `students_not_enrolled` int DEFAULT NULL,
  `video_names` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `summary`
--

LOCK TABLES `summary` WRITE;
/*!40000 ALTER TABLE `summary` DISABLE KEYS */;
INSERT INTO `summary` VALUES ('2024-01-09',30,1,1,'Military Training',1,'15:37:00','15:41:00',15,15,0,1,12,12,13,13,12,13,12,12,0,0,'[\"1_D29 - EDU 1.mp4\", \"1_D22 - EDU 1.mp4\"]'),('2024-01-09',31,2,2,'Emergency Evacuation',1,'15:51:00','15:56:00',15,13,2,1,13,11,11,13,13,12,13,13,0,0,'[\"2_D14 - EDU 2.mp4\", \"2_D7 - EDU 2.mp4\"]'),('2024-01-09',32,3,3,'Rapid Police Force',0,'15:55:00','16:00:00',15,10,5,2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'[\"3_D23 - EDU 3.mp4\", \"3_D32 - EDU 3.mp4\"]'),('2024-01-09',33,4,4,'Military Training',1,'16:00:00','16:05:00',15,15,0,1,12,12,12,13,12,12,13,13,0,0,'[\"4_D31 - EDU 4.mp4\", \"4_D30 - EDU 4.mp4\"]'),('2024-01-09',34,5,5,'Emergency Evacuation',0,'16:28:00','16:31:00',15,14,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'[\"5_D16 - BIG 1.mp4\", \"5_D20 - BIG 1.mp4\", \"5_D24 - BIG 1.mp4\", \"5_D27 - BIG 1.mp4\", \"5_D1 - BIG 1.mp4\"]'),('2024-01-09',35,6,6,'Rapid Police Force',1,'16:37:00','16:40:00',15,15,0,1,13,13,11,11,14,12,10,15,0,0,'[\"6_D16 - BIG 2.mp4\", \"6_D20 - BIG 2.mp4\", \"6_D24 - BIG 2.mp4\", \"6_D27 - BIG 2.mp4\", \"6_D1 - BIG 2.mp4\"]');
/*!40000 ALTER TABLE `summary` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-10 12:14:58
