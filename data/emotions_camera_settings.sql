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
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camera_settings`
--

LOCK TABLES `camera_settings` WRITE;
/*!40000 ALTER TABLE `camera_settings` DISABLE KEYS */;
INSERT INTO `camera_settings` VALUES ('2023-12-17',1,1,1,1,'one','121.mp4'),('2023-12-17',2,1,2,1,'two','recording.mp4'),('2023-12-17',3,1,3,1,'three','recording.mp4'),('2023-12-17',4,1,4,1,'four','recording.mp4'),('2023-12-17',5,1,5,1,'five','recording.mp4'),('2023-12-17',6,1,6,2,'one','recording.mp4'),('2023-12-17',7,1,7,2,'two','recording.mp4'),('2023-12-17',8,1,8,2,'three','recording.mp4'),('2023-12-17',9,1,9,2,'four','recording.mp4'),('2023-12-17',10,1,10,3,'one','recording.mp4'),('2023-12-17',11,1,11,3,'two','recording.mp4'),('2023-12-17',12,1,12,4,'one','recording.mp4'),('2023-12-17',13,1,13,4,'two','recording.mp4');
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

-- Dump completed on 2023-12-23 21:37:32
