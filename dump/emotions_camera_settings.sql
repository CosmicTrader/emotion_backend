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
-- Table structure for table `camera_settings`
--

DROP TABLE IF EXISTS `camera_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `camera_settings` (
  `date` date DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `camera_number` int NOT NULL,
  `room_number` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `rtsp` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `camera_number` (`camera_number`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camera_settings`
--

LOCK TABLES `camera_settings` WRITE;
/*!40000 ALTER TABLE `camera_settings` DISABLE KEYS */;
INSERT INTO `camera_settings` VALUES ('2024-01-10',1,1,21,7,'video','recording.mp4'),('2024-01-09',21,1,1,1,'D29 - EDU 1','rtsp://admin:malco@123@192.108.17.15:554'),('2024-01-09',22,1,2,1,'D22 - EDU 1','rtsp://admin:malco@123@192.108.17.11:554'),('2024-01-09',23,1,3,2,'D14 - EDU 2','rtsp://admin:malco@123@192.108.17.16:554'),('2024-01-09',24,1,4,2,'D7 - EDU 2','rtsp://admin:malco@123@192.108.17.13:554'),('2024-01-09',25,1,5,3,'D23 - EDU 3','rtsp://admin:malco@123@192.108.17.9:554'),('2024-01-09',26,1,6,3,'D32 - EDU 3','rtsp://admin:malco@123@192.108.17.8:554'),('2024-01-09',27,1,7,4,'D30 - EDU 4','rtsp://admin:malco@123@192.108.17.18:554'),('2024-01-09',28,1,8,4,'D31 - EDU 4','rtsp://admin:malco@123@192.108.17.12:554'),('2024-01-09',29,1,9,5,'D16 - BIG 1','rtsp://admin:malco@123@192.108.17.14:554'),('2024-01-09',30,1,10,5,'D20 - BIG 1','rtsp://admin:malco@123@192.108.17.7:554'),('2024-01-09',31,1,11,5,'D24 - BIG 1','rtsp://admin:malco@123@192.108.17.5:554'),('2024-01-09',32,1,12,5,'D27 - BIG 1','rtsp://admin:malco@123@192.108.17.2:554'),('2024-01-09',33,1,13,5,'D1 - BIG 1','rtsp://admin:malco@123@192.108.17.80:554'),('2024-01-09',34,1,14,6,'D16 - BIG 2','rtsp://admin:malco@123@192.108.17.6:554'),('2024-01-09',35,1,15,6,'D20 - BIG 2','rtsp://admin:malco@123@192.108.17.19:554'),('2024-01-09',36,1,16,6,'D24 - BIG 2','rtsp://admin:malco@123@192.108.17.17:554'),('2024-01-09',37,1,17,6,'D27 - BIG 2','rtsp://admin:malco@123@192.108.17.4:554'),('2024-01-09',38,1,18,6,'D1 - BIG 2','rtsp://admin:malco@123@192.108.17.3:554');
/*!40000 ALTER TABLE `camera_settings` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-01-10 12:14:57
