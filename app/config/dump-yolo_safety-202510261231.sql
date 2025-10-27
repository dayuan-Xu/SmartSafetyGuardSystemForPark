-- MySQL dump 10.13  Distrib 8.0.37, for Win64 (x86_64)
--
-- Host: localhost    Database: yolo_safety
-- ------------------------------------------------------
-- Server version	8.0.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alarm`
--

DROP TABLE IF EXISTS `alarm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alarm` (
  `alarm_id` bigint NOT NULL AUTO_INCREMENT,
  `camera_id` int NOT NULL,
  `alarm_type` int NOT NULL,
  `alarm_status` int DEFAULT NULL,
  `alarm_time` datetime NOT NULL,
  `snapshot_url` varchar(255) NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `alarm_end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`alarm_id`),
  KEY `ix_alarm_alarm_id` (`alarm_id`),
  KEY `ix_alarm_camera_id` (`camera_id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm`
--

LOCK TABLES `alarm` WRITE;
/*!40000 ALTER TABLE `alarm` DISABLE KEYS */;
INSERT INTO `alarm` VALUES (1,1,0,3,'2024-02-01 08:30:00','/snapshots/alarm1.jpg','2024-02-01 08:30:00','2024-02-01 09:15:00',NULL),(2,2,0,3,'2024-02-01 09:45:00','/snapshots/alarm2.jpg','2024-02-01 09:45:00','2024-02-01 10:30:00',NULL),(3,3,2,1,'2024-02-01 10:15:00','/snapshots/alarm3.jpg','2024-02-01 10:15:00','2024-02-01 10:20:00',NULL),(4,4,2,2,'2024-02-01 14:20:00','/snapshots/alarm4.jpg','2024-02-01 14:20:00','2024-02-01 14:25:00',NULL),(5,1,2,0,'2024-02-01 15:50:00','/snapshots/alarm5.jpg','2024-02-01 15:50:00','2024-02-01 15:50:00',NULL),(37,6,0,0,'2025-09-18 16:38:48','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/6_2025-09-18 16:38:46.jpg','2025-09-18 16:38:38','2025-09-18 16:38:38',NULL),(38,1,1,0,'2025-09-25 11:14:59','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/09/25/e93a17a5-30d8-4464-aa79-bcf3d05576ee.jpg','2025-09-25 11:13:35','2025-09-25 11:13:35',NULL),(39,3,1,0,'2025-09-25 13:53:41','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/09/25/32da11e0-d646-441f-9270-224a09f68d6d.jpg','2025-09-25 13:53:02','2025-09-25 13:53:02',NULL),(40,2,0,0,'2025-10-21 14:19:35','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/8f7a368f-a71d-4ce1-bcbb-895a2fac3fba.jpghttps://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/909e3bfc-1365-416d-ad8a-37c9fed0b56b.jpg,','2025-10-21 14:16:58','2025-10-21 14:16:58',NULL),(41,2,0,0,'2025-10-21 14:33:13','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/dffc764a-ff2f-4a18-9759-c1d135a04ffb.jpghttps://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/7ae6d0c8-f551-44dc-a303-e43e4c7da8c9.jpg,','2025-10-21 14:32:40','2025-10-21 14:32:40',NULL),(42,4,2,0,'2025-10-21 14:53:00','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/053c913f-a36c-4d0f-923f-8ebe7bc72e78.jpg','2025-10-21 14:50:59','2025-10-21 14:53:04','2025-10-21 14:53:04'),(43,4,2,0,'2025-10-21 14:53:16','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/8be27441-d3ff-4d70-8dcd-e6a6bedc2b50.jpg','2025-10-21 14:50:59','2025-10-21 14:53:22','2025-10-21 14:53:22'),(44,4,2,0,'2025-10-21 14:54:10','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/a6c1ce9c-ea64-4fd5-8dfd-d55277199fad.jpg','2025-10-21 14:50:59','2025-10-21 14:54:31','2025-10-21 14:54:31'),(45,4,2,0,'2025-10-21 14:55:07','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/6a4b8a3d-4194-469d-92c9-f2f6c7337291.jpg','2025-10-21 14:50:59','2025-10-21 14:55:09','2025-10-21 14:55:09'),(46,4,2,0,'2025-10-21 14:55:21','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/821865db-33e3-4f06-a7b1-9764e01c2c6f.jpg','2025-10-21 14:50:59','2025-10-21 14:50:59',NULL),(47,3,1,0,'2025-10-21 14:57:09','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/7ec9edca-ffa8-41fd-a5b0-76728f700307.jpg','2025-10-21 14:56:41','2025-10-21 14:56:41',NULL),(48,2,0,0,'2025-10-21 17:22:40','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/9060652d-21da-4a7b-b787-0f46ac5fe467.jpghttps://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/d9477491-24f9-4323-a8b1-c5bd0770e81b.jpg,','2025-10-21 17:22:11','2025-10-21 17:22:11',NULL),(49,2,0,0,'2025-10-21 19:07:12','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/e692fabc-4859-476d-9653-8705f5e26843.jpg','2025-10-21 19:06:59','2025-10-21 19:06:59',NULL),(50,2,0,0,'2025-10-21 19:13:13','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/21/0c5de948-9f23-4d20-ad6e-6bc3bedc4df0.jpg','2025-10-21 19:08:18','2025-10-21 19:08:18',NULL),(51,3,1,0,'2025-10-22 21:25:38','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/22/16657d25-398d-4e6f-acf5-07543856f5d9.jpg','2025-10-22 21:01:19','2025-10-22 21:01:19',NULL),(52,1,1,0,'2025-10-22 21:25:39','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/22/765ff021-0f69-4916-aec8-3f951e3e5808.jpg','2025-10-22 21:01:19','2025-10-22 21:25:54','2025-10-22 21:25:54'),(53,2,0,0,'2025-10-22 21:46:58','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/22/74af34b0-2014-432a-9c04-66fc1e691af5.jpg','2025-10-22 21:01:19','2025-10-22 21:01:19',NULL),(54,1,1,0,'2025-10-22 21:47:00','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/22/f6df28ca-2b7a-4f55-b6fa-8e514ae97018.jpg','2025-10-22 21:01:19','2025-10-22 21:47:38','2025-10-22 21:47:38'),(55,1,1,0,'2025-10-23 16:00:40','https://yolo-park-safety-guard.oss-cn-beijing.aliyuncs.com/2025/10/23/9c3e3193-4300-4b1d-aa0c-d7c72bb8d795.jpg','2025-10-23 15:54:33','2025-10-23 15:54:33',NULL);
/*!40000 ALTER TABLE `alarm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alarm_handle_record`
--

DROP TABLE IF EXISTS `alarm_handle_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alarm_handle_record` (
  `handle_id` bigint NOT NULL AUTO_INCREMENT,
  `alarm_id` bigint NOT NULL,
  `handle_time` datetime NOT NULL,
  `handler_user_id` int NOT NULL,
  `handle_action` int NOT NULL,
  `handle_content` text,
  `handle_attachment_url` varchar(255) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`handle_id`),
  KEY `ix_alarm_handle_record_handle_id` (`handle_id`),
  KEY `ix_alarm_handle_record_alarm_id` (`alarm_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alarm_handle_record`
--

LOCK TABLES `alarm_handle_record` WRITE;
/*!40000 ALTER TABLE `alarm_handle_record` DISABLE KEYS */;
INSERT INTO `alarm_handle_record` VALUES (1,1,'2024-02-01 08:40:00',2,1,'派单给安保人员张三前往处理',NULL,'2024-02-01 08:40:00','2024-02-01 08:40:00'),(2,1,'2024-02-01 09:15:00',3,2,'已提醒施工人员佩戴安全帽，现场照片见附件','/attachments/alarm1_solved.jpg','2024-02-01 09:15:00','2024-02-01 09:15:00'),(3,2,'2024-02-01 09:50:00',2,1,'派单给仓库管理员李四处理',NULL,'2024-02-01 09:50:00','2024-02-01 09:50:00'),(4,2,'2024-02-01 10:30:00',4,2,'已要求进入仓库人员穿戴反光衣','/attachments/alarm2_solved.jpg','2024-02-01 10:30:00','2024-02-01 10:30:00'),(5,3,'2024-02-01 10:20:00',1,0,'经核实为误报，因摄像头角度偏移导致',NULL,'2024-02-01 10:20:00','2024-02-01 10:20:00'),(6,4,'2024-02-01 14:25:00',2,1,'派单给消防巡查员王五紧急处理',NULL,'2024-02-01 14:25:00','2024-02-01 14:25:00');
/*!40000 ALTER TABLE `alarm_handle_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `camera_info`
--

DROP TABLE IF EXISTS `camera_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `camera_info` (
  `camera_id` int NOT NULL AUTO_INCREMENT,
  `camera_name` varchar(64) NOT NULL,
  `park_area_id` int NOT NULL,
  `install_position` varchar(64) NOT NULL,
  `rtsp_url` varchar(255) NOT NULL,
  `analysis_mode` int NOT NULL,
  `camera_status` int DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`camera_id`),
  KEY `ix_camera_info_camera_id` (`camera_id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camera_info`
--

LOCK TABLES `camera_info` WRITE;
/*!40000 ALTER TABLE `camera_info` DISABLE KEYS */;
INSERT INTO `camera_info` VALUES (1,'id为1的摄像头的新名字',1,'东门岗亭上方','local:all.mp4',1,1,'2024-01-10 00:00:00','2025-10-23 16:00:40'),(2,'仓库区域摄像头',2,'仓库门口','local:helmet_vest.mp4',2,1,'2024-01-10 00:00:00','2025-10-22 21:46:52'),(3,'危险品存放区摄像头',3,'存放区围栏处','local:person_vehicle.mp4',3,1,'2024-01-10 00:00:00','2025-10-22 21:52:00'),(4,'消防通道摄像头',1,'消防通道入口','local:fire_smoke.mp4',4,1,'2024-01-11 00:00:00','2025-10-22 21:46:52'),(5,'电梯轿厢摄像头',3,'3号楼1单元电梯内','rtsp://192.168.1.106:554/stream',1,1,'2024-01-13 10:30:00','2025-10-22 21:47:29'),(6,'小区东门摄像头',1,'东门岗亭外侧','rtsp://192.168.1.107:554/stream',3,1,'2024-01-14 14:00:00','2025-10-22 21:48:18'),(7,'地下车库摄像头',2,'地下负一层拐角','rtsp://192.168.1.108:554/stream',2,1,'2024-01-15 09:15:00','2025-10-22 21:48:53'),(8,'单元门口摄像头',3,'5号楼2单元门口','rtsp://192.168.1.109:554/stream',1,1,'2024-01-16 16:45:00','2025-10-22 21:48:23'),(9,'绿化带摄像头',1,'中心花园北侧','rtsp://192.168.1.110:554/stream',4,1,'2024-01-17 11:20:00','2025-10-22 21:26:15'),(10,'垃圾站摄像头',2,'生活垃圾站旁','rtsp://192.168.1.111:554/stream',2,1,'2024-01-18 07:30:00','2025-10-22 21:26:15'),(11,'健身区摄像头',3,'室外健身器材区','rtsp://192.168.1.112:554/stream',1,1,'2024-01-19 15:50:00','2025-10-22 21:26:15'),(12,'物业办公室摄像头',1,'物业前台内侧','rtsp://192.168.1.113:554/stream',3,1,'2024-01-20 13:10:00','2025-10-22 21:26:15'),(13,'快递柜摄像头',2,'智能快递柜正面','rtsp://192.168.1.114:554/stream',2,1,'2024-01-21 10:05:00','2025-10-22 21:26:15'),(14,'儿童游乐区摄像头',3,'滑梯旁','rtsp://192.168.1.115:554/stream',1,1,'2024-01-22 09:40:00','2025-10-22 21:26:16'),(15,'西门岗亭摄像头',1,'西门岗亭内侧','rtsp://192.168.1.116:554/stream',4,1,'2024-01-23 16:25:00','2025-10-22 21:26:16'),(16,'水泵房摄像头',2,'地下水泵房门口','rtsp://192.168.1.117:554/stream',2,1,'2024-01-24 14:50:00','2025-10-22 21:26:16'),(17,'配电房摄像头',3,'配电房外侧','rtsp://192.168.1.118:554/stream',1,1,'2024-01-25 11:15:00','2025-10-22 21:26:16'),(18,'非机动车车库摄像头',1,'非机动车出入口','rtsp://192.168.1.119:554/stream',3,1,'2024-01-26 08:30:00','2025-10-22 21:26:16'),(19,'监控中心摄像头',2,'监控大屏前','rtsp://192.168.1.120:554/stream',1,1,'2024-01-27 15:40:00','2025-10-22 21:26:15'),(20,'会所大堂摄像头',3,'会所入口处','rtsp://192.168.1.121:554/stream',1,1,'2024-01-28 12:20:00','2025-10-22 21:26:15'),(21,'消防控制室摄像头',1,'消防控制操作台','rtsp://192.168.1.122:554/stream',4,1,'2024-01-29 10:50:00','2025-10-22 21:26:16'),(22,'南门入口摄像头',2,'南门主通道','rtsp://192.168.1.123:554/stream',2,1,'2024-01-30 09:10:00','2025-10-22 21:26:15'),(23,'天台入口摄像头',3,'10号楼天台门','rtsp://192.168.1.124:554/stream',1,1,'2024-01-31 17:30:00','2025-10-22 21:26:15'),(24,'垃圾分拣站摄像头',1,'垃圾分类投放点','rtsp://192.168.1.125:554/stream',3,1,'2024-02-01 14:20:00','2025-10-22 21:26:15'),(25,'道闸系统摄像头',2,'车辆道闸旁','rtsp://192.168.1.126:554/stream',2,1,'2024-02-02 11:45:00','2025-10-22 21:26:15'),(26,'电梯机房摄像头',3,'电梯机房内','rtsp://192.168.1.127:554/stream',1,1,'2024-02-03 08:55:00','2025-10-22 21:26:15'),(27,'小区围墙摄像头',1,'北侧围墙中段','rtsp://192.168.1.128:554/stream',4,1,'2024-02-04 16:10:00','2025-10-22 21:26:15'),(28,'商铺门口摄像头',2,'沿街商铺前','rtsp://192.168.1.129:554/stream',2,1,'2024-02-05 13:30:00','2025-10-22 21:26:15'),(29,'活动中心摄像头',3,'活动中心大厅','rtsp://192.168.1.130:554/stream',1,1,'2024-02-06 10:20:00','2025-10-22 21:26:15'),(30,'岗亭外侧摄像头',1,'北门岗亭外部','rtsp://192.168.1.131:554/stream',3,1,'2024-02-07 09:05:00','2025-10-22 21:26:15'),(31,'化粪池区域摄像头',2,'化粪池检修口旁','rtsp://192.168.1.132:554/stream',2,1,'2024-02-08 15:50:00','2025-10-22 21:26:15'),(32,'仓库门口摄像头',3,'物业仓库入口','rtsp://192.168.1.133:554/stream',1,1,'2024-02-09 12:15:00','2025-10-22 21:26:15'),(33,'充电桩区域摄像头',1,'电动汽车充电桩旁','rtsp://192.168.1.134:554/stream',4,1,'2024-02-10 14:40:00','2025-10-22 21:26:15');
/*!40000 ALTER TABLE `camera_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `park_area`
--

DROP TABLE IF EXISTS `park_area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `park_area` (
  `park_area_id` int NOT NULL AUTO_INCREMENT,
  `park_area` varchar(64) NOT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`park_area_id`),
  UNIQUE KEY `park_area` (`park_area`),
  KEY `ix_park_area_park_area_id` (`park_area_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `park_area`
--

LOCK TABLES `park_area` WRITE;
/*!40000 ALTER TABLE `park_area` DISABLE KEYS */;
INSERT INTO `park_area` VALUES (1,'A区的新名字','A区的新名字的备注','2024-01-10 00:00:00','2025-10-26 12:28:21'),(2,'B区的新名字',NULL,'2024-01-10 00:00:00','2025-10-01 15:32:25'),(3,'C区','C区的备注','2024-01-10 00:00:00','2025-10-26 12:28:39');
/*!40000 ALTER TABLE `park_area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `user_name` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL,
  `user_role` int DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `gender` tinyint DEFAULT '1',
  `phone` varchar(11) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_name`),
  UNIQUE KEY `user_unique` (`phone`),
  KEY `ix_user_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'王建国（大）','王建国','$2b$12$8vxTelOU184OMatvlbPu1.pq.CjZ01Xr0/j.giDs91B98CgVJU9b2',0,'2024-01-01 00:00:00','2025-09-26 16:25:38',1,'12345678901'),(2,'admin2','陈曦','encrypted_admin1243',0,'2024-01-01 00:00:00','2024-01-01 00:00:00',1,'12345678902'),(3,'security_manager1','李婷','encrypted_security456',1,'2024-01-02 00:00:00','2024-01-02 00:00:00',1,'12345678903'),(4,'security_manager2','赵亮','encrypted_security457',1,'2024-01-03 00:00:00','2024-01-03 00:00:00',1,'12345678904'),(5,'operator_1','张伟','encrypted_op789',2,'2024-01-03 00:00:00','2024-01-03 00:00:00',1,'12345678905'),(6,'operator_2','刘芳','encrypted_op012',2,'2024-01-04 00:00:00','2024-01-04 00:00:00',1,'12345678906'),(7,'operator_3','黄伟','encrypted_op013',2,'2024-01-04 00:00:00','2024-01-04 00:00:00',1,'12345678907'),(8,'operator_4','周敏','encrypted_op012',2,'2024-01-04 00:00:00','2024-01-04 00:00:00',1,'12345678908'),(10,'admin','待定','$2b$12$0wPNq96AExS6QbYivAtmW.bTURFzQY2JVmVL.Skc.qwaUdm.pW0Sa',0,'2025-09-25 16:53:28','2025-09-25 16:53:28',1,'15083440074'),(25,'string','待定','$2b$12$.WMfx.9PoI05UicQpD7LluiaSEx9/EI2rC6rr7IfT5VfDpA9HlZ5S',0,'2025-09-25 17:23:37','2025-09-25 17:23:37',1,'15083440073');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'yolo_safety'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-26 12:31:34
