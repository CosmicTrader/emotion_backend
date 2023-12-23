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
-- Table structure for table `emotions`
--

DROP TABLE IF EXISTS `emotions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emotions` (
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `id` int NOT NULL AUTO_INCREMENT,
  `summary_id` int DEFAULT NULL,
  `student_id` int NOT NULL,
  `subject` varchar(100) DEFAULT NULL,
  `anger` int DEFAULT NULL,
  `disgust` int DEFAULT NULL,
  `fear` int DEFAULT NULL,
  `happy` int DEFAULT NULL,
  `neutral` int DEFAULT NULL,
  `sadness` int DEFAULT NULL,
  `surprise` int DEFAULT NULL,
  `unknown` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `summary_id` (`summary_id`),
  CONSTRAINT `emotions_ibfk_1` FOREIGN KEY (`summary_id`) REFERENCES `emotion_summary` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `emotions`
--

LOCK TABLES `emotions` WRITE;
/*!40000 ALTER TABLE `emotions` DISABLE KEYS */;
INSERT INTO `emotions` VALUES ('2023-12-21 14:52:57',1,1,1,'basic',10,10,10,10,10,10,10,30),('2023-12-21 14:52:57',2,1,2,'basic',10,10,10,10,10,10,10,30),('2023-12-21 14:52:57',3,1,3,'basic',10,10,10,10,10,10,10,30);
/*!40000 ALTER TABLE `emotions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-23 21:37:35
