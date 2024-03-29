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
-- Table structure for table `session_details`
--

DROP TABLE IF EXISTS `session_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session_details` (
  `date` date DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `course_id` int DEFAULT NULL,
  `course_name` varchar(100) NOT NULL,
  `course_description` varchar(1000) NOT NULL,
  `room_number` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `session_details_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course_details` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_details`
--

LOCK TABLES `session_details` WRITE;
/*!40000 ALTER TABLE `session_details` DISABLE KEYS */;
INSERT INTO `session_details` VALUES ('2024-01-09',24,1,1,'Military Training','Basic Military Training',1,'2024-01-09','2024-01-10','15:37:00','15:41:00'),('2024-01-09',25,2,2,'Emergency Evacuation','Basic Emergency Evacuation',2,'2024-01-09','2024-01-10','15:51:00','15:56:00'),('2024-01-09',26,3,3,'Rapid Police Force','Rapid Police Force RPF',3,'2024-01-09','2024-01-10','15:55:00','16:00:00'),('2024-01-09',27,4,1,'Military Training','Basic Military Training',4,'2024-01-09','2024-01-10','16:00:00','16:05:00'),('2024-01-09',28,5,2,'Emergency Evacuation','Basic Emergency Evacuation',5,'2024-01-09','2024-01-10','16:28:00','16:31:00'),('2024-01-09',29,6,3,'Rapid Police Force','Rapid Police Force RPF',6,'2024-01-09','2024-01-10','17:05:00','17:10:00'),('2024-01-09',30,7,3,'Rapid Police Force','Rapid Police Force RPF',7,'2024-01-09','2024-01-10','00:42:00','00:44:00');
/*!40000 ALTER TABLE `session_details` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-10 12:14:59
