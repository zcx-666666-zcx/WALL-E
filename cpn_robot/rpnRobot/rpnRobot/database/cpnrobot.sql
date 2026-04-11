-- MySQL dump 10.13  Distrib 9.3.0, for macos15 (x86_64)
--
-- Host: localhost    Database: cpnrobot
-- ------------------------------------------------------
-- Server version	9.3.0

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
-- Table structure for table `command`
--

DROP TABLE IF EXISTS `command`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `command` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID，唯一且自增',
  `command_name` varchar(100) DEFAULT NULL COMMENT '指令名称',
  `command_code` varchar(50) DEFAULT NULL COMMENT '指令代码',
  `execution_status` varchar(20) DEFAULT NULL COMMENT '执行状态',
  `time` datetime DEFAULT NULL COMMENT '执行时间',
  `machines` varchar(100) DEFAULT NULL COMMENT '设备名称',
  `user_id` int DEFAULT NULL COMMENT '用户ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='指令执行记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `command`
--

LOCK TABLES `command` WRITE;
/*!40000 ALTER TABLE `command` DISABLE KEYS */;
/*!40000 ALTER TABLE `command` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contract_machine`
--

DROP TABLE IF EXISTS `contract_machine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contract_machine` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID，唯一且自增',
  `machines` varchar(20) NOT NULL COMMENT '被绑设备名称',
  `connectionId` varchar(10) NOT NULL COMMENT '被绑定设备号',
  `user_id` int NOT NULL COMMENT '用户ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contract_machine`
--

LOCK TABLES `contract_machine` WRITE;
/*!40000 ALTER TABLE `contract_machine` DISABLE KEYS */;
INSERT INTO `contract_machine` VALUES (1,'测试设备1','00001',1);
/*!40000 ALTER TABLE `contract_machine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contract_user`
--

DROP TABLE IF EXISTS `contract_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contract_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID，唯一且自增',
  `contract_name` varchar(20) NOT NULL COMMENT '被绑定人名称',
  `contract_phone_number` varchar(11) NOT NULL COMMENT '被绑定人手机号',
  `user_id` int NOT NULL COMMENT '用户ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='联系人表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contract_user`
--

LOCK TABLES `contract_user` WRITE;
/*!40000 ALTER TABLE `contract_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `contract_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_message`
--

DROP TABLE IF EXISTS `device_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `msg` text,
  `nonce` varchar(32) DEFAULT NULL,
  `signature` varchar(128) DEFAULT NULL,
  `push_time` bigint DEFAULT NULL,
  `message_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_message`
--

LOCK TABLES `device_message` WRITE;
/*!40000 ALTER TABLE `device_message` DISABLE KEYS */;
INSERT INTO `device_message` VALUES (1,'{\"dev_name\":\"WALEE_1\",\"at\":1772015963465,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','I5OAsljW','tjh69UjfhSh0d3ZB1fxyaQ==',1772015963473,'e80e8b77bfd640c2af54ea96e69e033b'),(2,'{\"dev_name\":\"WALEE_1\",\"at\":1772015963498,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','gmbKlKHl','d7b0JxtAwoHZ0qmPXmklhw==',1772015963511,'150141ce909a44f0959a753865cfd10d'),(3,'{\"dev_name\":\"WALEE_1\",\"at\":1772015936236,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','Fau8qcPV','ByJnVH58UAjiyJs7oazDZQ==',1772015936249,'09ed3301d0204b1083ffbd490db67b0d'),(4,'{\"dev_name\":\"WALEE_1\",\"at\":1772015985257,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','9d68LTJe','fFAM4IuUWzN/0W0NUeQnzQ==',1772015985266,'537079395e0e48c58a8c3abf67f38abc'),(5,'{\"dev_name\":\"WALEE_1\",\"at\":1772015986904,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','bC4Xtb9H','LQitixIIYpNpPTKs3V0vUg==',1772015986915,'77cfa7c86ef24401a802d77379ccfa03'),(6,'{\"dev_name\":\"WALEE_1\",\"at\":1772015612489,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','KTADYoXy','41npv1ITXD8DvTr34zlLCw==',1772015612501,'8fca55806c874c01ba47af626a860660'),(7,'{\"dev_name\":\"WALEE_1\",\"at\":1772015406496,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','bT7na32Y','gghAfAOjcQPRBQmgUfrFxA==',1772015406509,'aec51172d6964bb6a761d99333f49f8f'),(8,'{\"dev_name\":\"WALEE_1\",\"at\":1772016134593,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','yanEsp6P','po3udQ43pMfZD17OCo4MBA==',1772016134607,'9408fb8d5f164ceebbb0cc6f8ce57b11'),(9,'{\"dev_name\":\"WALEE_1\",\"at\":1772016604491,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','zjnolwrW','95qlhXfcBwXHz8SN5Sl9Og==',1772016604506,'603439684d194d138aa083b1548778c3'),(10,'{\"dev_name\":\"WALEE_1\",\"at\":1772016604417,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','fO8GTctO','1HBDru2XRPsmyzDJDSr6Pg==',1772016604430,'b1229b1b18dc414892066a2b77fba428'),(11,'{\"dev_name\":\"WALEE_1\",\"at\":1772016604372,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','30UShTdm','5ZjfwwEv44cPLF/mj/N5Fw==',1772016604389,'d59f8ae06f044641a554a1b6e4598991'),(12,'{\"dev_name\":\"WALEE_1\",\"at\":1772016616565,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','1TWPrhXx','NCTUVV9ySm7F7PqZ7FCfrA==',1772016616579,'e487a63db4174424878e6830c13e9d2a'),(13,'{\"dev_name\":\"WALEE_1\",\"at\":1772016659328,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','fRXvWlmB','2dCJxu/JugCr7y6uPBZUBQ==',1772016659334,'6f6902dbe1a04be6a8e2c1a7e45d7f4e'),(14,'{\"dev_name\":\"WALEE_1\",\"at\":1772016659370,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','zufmMbMm','P1A8csD3e9A/IqATLpnh5Q==',1772016659381,'18b8abb57de34b14aa7b9bb35a1c9885'),(15,'{\"dev_name\":\"WALEE_1\",\"at\":1772016659565,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','HHPfJOw7','2oGbaqhwf/LN/7U4X9YHOw==',1772016659580,'2b34a20a08e34223b251eaa0e61b7c31'),(16,'{\"dev_name\":\"WALEE_1\",\"at\":1772016674418,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','N9boMoMV','A0icuPFLBaknje/siOSVuw==',1772016674424,'a24349e94f51448e89ddf31c97bdbf25'),(17,'{\"dev_name\":\"WALEE_1\",\"at\":1772016717851,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','Rq4EAZ0x','745g2aXWC8JMnPc6tz9PJg==',1772016717862,'6c5f40313c8c4e4d8e1604b1617396c3'),(18,'{\"dev_name\":\"WALEE_1\",\"at\":1772016777903,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','KUE3OhWJ','OCnCLA2c3dRBUJGrTueNWg==',1772016777908,'2c68c29c20de4b77b7d1485f87fa69a1'),(19,'{\"dev_name\":\"WALEE_1\",\"at\":1772019622094,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','P9uVe8pr','L5A9H4cyqOojUpUlKPXKNQ==',1772019622101,'bb0f4cdd333d483092e81b5472dcec64'),(20,'{\"dev_name\":\"WALEE_1\",\"at\":1772019622172,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','TAP2J594','8oSqzZpsg2jXHxAAsEhFug==',1772019622177,'59d5d7acd6bc44a7b37cdcfa36e7701f'),(21,'{\"dev_name\":\"WALEE_1\",\"at\":1772019682105,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','nq4XXmmW','Y1oiVsn9Q2FZLr73pcZGSQ==',1772019682111,'bbd1668f73c044198d86b3a254d7a399'),(22,'{\"dev_name\":\"WALEE_1\",\"at\":1772019865001,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','Hw4RLKmu','GWE5Q0mJvsfcJkBv2LAhiA==',1772019865007,'9ec401f099c541f38f15bb916153c98b'),(23,'{\"dev_name\":\"WALEE_1\",\"at\":1772019865073,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','WW2rBzpP','ZjrNOaTu8PvUs9JhamRJXQ==',1772019865078,'2b0279c1d06943aeaae256debbdc116e'),(24,'{\"dev_name\":\"WALEE_1\",\"at\":1772019864967,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','kD3cCmFp','bAYpjxTeZfzYqtewWzFu/g==',1772019864972,'b9f86fb522a9474298e7413ccdbd2082'),(25,'{\"dev_name\":\"WALEE_1\",\"at\":1772019925010,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','qYeqb8DL','gF8MZLj4no97x8Exiv/OKA==',1772019925015,'d8182351a9bd4f5c9cf07ca89d326859'),(26,'{\"dev_name\":\"WALEE_1\",\"at\":1772020045011,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"ceshi\",\"value\":666}','zxwAhbWQ','Y8PJT3g8oxzttNLqpiUiSA==',1772020045016,'75a7454c9d0b40cb8e4c695d2797e91b'),(27,'{\"dev_name\":\"WALEE_1\",\"at\":1772020280308,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','yzuryvMJ','mKePgG6FUScrcLey24cwsQ==',1772020280312,'43d31e68829d4f00a68a1de12048e0e5'),(28,'{\"dev_name\":\"WALEE_1\",\"at\":1772020070822,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','TKWtkdBx','oDpt7eNCD8KAoasvyoaiVA==',1772020070828,'1a8c5475271249f4ab48130fa0ba3c90'),(29,'{\"dev_name\":\"WALEE_1\",\"at\":1772020280413,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','vbDpGG4y','m1glev2i7AbYZRbaYQ6Jiw==',1772020280417,'3744744e0e0547a0b93daf3fcb345db9'),(30,'{\"dev_name\":\"WALEE_1\",\"at\":1772020280413,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.1}','FAbSXvpH','FlNR6ovPXre1gM76G4Di7g==',1772020280420,'b389fb6f86c0479baeba1d7cb867f9ea'),(31,'{\"dev_name\":\"WALEE_1\",\"at\":1772020280413,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":51.2}','y8YQI66O','YBY4NAS1BU/xrO03FX4fKw==',1772020280423,'276e3739ab85450d9be1d9bd94bddfb1'),(32,'{\"dev_name\":\"WALEE_1\",\"at\":1772020280413,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":16}','4rXV4aoC','X0dt8ePRy7jkj6CD/SfHBQ==',1772020280419,'2cd0a6d2fee841c0b1977d4d43171efa'),(33,'{\"dev_name\":\"WALEE_1\",\"at\":1772020340354,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":63}','JoF15yRL','GUqT0fnUimK4hAhW9iXO9Q==',1772020340361,'81376b63bdbc4c9ab5d717acd55595ed'),(34,'{\"dev_name\":\"WALEE_1\",\"at\":1772020340354,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','GxI31LFf','UBNyWgUpTUGbw8Kfw8gV1g==',1772020340358,'e2b655d496314a689b9c31a00206082b'),(35,'{\"dev_name\":\"WALEE_1\",\"at\":1772020340354,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.7}','pBU1KPM5','NQ1lEKaHfi7dvQUaXJKgfw==',1772020340360,'3cf102dc4be14b17915ac880ca71383b'),(36,'{\"dev_name\":\"WALEE_1\",\"at\":1772020352701,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','hOExsf0J','yxi3qychU8FSxZx/1ZmmEA==',1772020352704,'8024fae0defb4e4a8eb8b3dff99ac947'),(37,'{\"dev_name\":\"WALEE_1\",\"at\":1772104873379,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":100}','TTLZuizs','h0BJvfRhhZtxNtRhkA3Aig==',1772104873403,'8a02ad09f66c4a59b78a1d50b02183fc'),(38,'{\"dev_name\":\"WALEE_1\",\"at\":1772104873379,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":40.4}','s1Z1F2yA','0/LFE8WWLYiVzBSAVYw8Yw==',1772104873383,'d4e4dc8382fb4dd68137fa4bb6b7672b'),(39,'{\"dev_name\":\"WALEE_1\",\"at\":1772104873379,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','njWHJHk0','Cam3w1xcg445RUjetk2t/w==',1772104873400,'94781d2e325546cb8577213dba497218'),(40,'{\"dev_name\":\"WALEE_1\",\"at\":1772104873379,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.1}','jHVk6KiA','G0768YRtyyKzY0xv6qrGlQ==',1772104873399,'13338e7d6b014c2dbd9dee0c07ab0bcd'),(41,'{\"dev_name\":\"WALEE_1\",\"at\":1772104933325,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":false}','WbGIiifZ','Kpitp0agJBZxN5HB/Yzrog==',1772104933334,'e327ce3d57944b6a91551d287d5d6375'),(42,'{\"dev_name\":\"WALEE_1\",\"at\":1772104933325,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":87}','QWktqdrz','CDCfWSdePGUpz3/BqT13qw==',1772104933336,'57a255e9d1e74c05a20fa630a3a40483'),(43,'{\"dev_name\":\"WALEE_1\",\"at\":1772104933325,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":17}','ojC07ada','yQpND1l9aC4RwK7d7cf71w==',1772104933317,'11e458c3d6f24d97816e96df13c44d53'),(44,'{\"dev_name\":\"WALEE_1\",\"at\":1772104939348,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','ehIrmRBr','G4xWhIqrGLQpfQiQeoUkVQ==',1772104939345,'46c7af8c1de048929f6e205868d1000d'),(45,'{\"dev_name\":\"WALEE_1\",\"at\":1772164257779,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','08JKVOWi','7QJXfIDIcXw6wshDn7mzUA==',1772164257778,'ea5c01145dcc4a53b61a12e2ef3625bc'),(46,'{\"dev_name\":\"WALEE_1\",\"at\":1772164257779,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":16}','bs6zKoSV','RJ9hA72zovAkYOA59vybpQ==',1772164257774,'97cf254e6f4c4569a3332114cec04182'),(47,'{\"dev_name\":\"WALEE_1\",\"at\":1772164257779,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":51.9}','yyZg1m1e','EwQgmbQdzJoaRW151wQ2OA==',1772164257778,'bbd97d37e4b947d78a9aeeb17af3b9a7'),(48,'{\"dev_name\":\"WALEE_1\",\"at\":1772164257779,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.2}','vFielOJ7','NYgu9RXQdvybV48ZHUZdGQ==',1772164257776,'3d98d20d46c44a39b35ea6c3de5cfa77'),(49,'{\"dev_name\":\"WALEE_1\",\"at\":1772164317704,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":15}','plv5yBF3','BKa/Xqf8kTGKfzjotldEiQ==',1772164317701,'922eacff3b464b6dabaa6c1cb72c114d'),(50,'{\"dev_name\":\"WALEE_1\",\"at\":1772174293417,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":18}','4nUn24YR','su9ClBzpGCBUwgshrbSfTA==',1772174293415,'f60f73de3ab846399a9c8e8d9f8b7f58'),(51,'{\"dev_name\":\"WALEE_1\",\"at\":1772174293343,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','Y0qUBQu1','pJfhKW3Lyz2PCAQGsNLkVg==',1772174293343,'d6c8aaa20a9d4ac7b54836a8c8353d5a'),(52,'{\"dev_name\":\"WALEE_1\",\"at\":1772174293417,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','iJJe5Xls','ytdYymUwFss6UnH6n8tGNw==',1772174293426,'aad67b02edd5430faaab46f5d9703243'),(53,'{\"dev_name\":\"WALEE_1\",\"at\":1772174293417,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":99}','OmKiA7eX','pWRorYETelqDxkq2TdQsOA==',1772174293416,'176f8960e5b041b4885b3c7f719b32b0'),(54,'{\"dev_name\":\"WALEE_1\",\"at\":1772174353347,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','KQAtP45i','HHG8RjfbSEZNsj9ipZuxPg==',1772174353351,'c7d8ce44df1448d88b41a4a2a4bfc566'),(55,'{\"dev_name\":\"WALEE_1\",\"at\":1772174353347,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":58.3}','TPwwdNAi','oO9a0juKDMUmKNJYhogQvQ==',1772174353343,'16091521850341e68cffda67e86c7ae7'),(56,'{\"dev_name\":\"WALEE_1\",\"at\":1772174353347,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":19}','NTaXlt56','IPHmattddERgNf6s0JCPGQ==',1772174353342,'dbe2b967132b4c528ec758f5f2975ee0'),(57,'{\"dev_name\":\"WALEE_1\",\"at\":1772174376832,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','HuEtBGqD','PUBLhFb/RzIXcoOHbfPJ2g==',1772174376834,'01249354cc134086affb377a10d92a4f'),(58,'{\"dev_name\":\"WALEE_1\",\"at\":1772175902541,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":13}','LXAxnV7A','zWQtSZAZ5taTzsfmEvemIw==',1772175902542,'5c7a59f5dc8f43548ccef1eb6b26d633'),(59,'{\"dev_name\":\"WALEE_1\",\"at\":1772175902541,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":37.0}','QixrNtRQ','Nl6LiZC/DnQtjpZYwGM9kw==',1772175902547,'bd2856e16c87493fb7fbd0a08d15ef0d'),(60,'{\"dev_name\":\"WALEE_1\",\"at\":1772175902460,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','ihp5L844','lnkXGhQa1E2h0uaxlVHbhw==',1772175902461,'e3a0cbc94cb84214ae5772cba9e2d88f'),(61,'{\"dev_name\":\"WALEE_1\",\"at\":1772175902541,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":77}','HAyCxnnM','gXkhTSIZ1bAmBaHPFmDFmQ==',1772175902540,'9f97459ed92045798e20cb73f4ce0d3c'),(62,'{\"dev_name\":\"WALEE_1\",\"at\":1772175902541,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":58.5}','ZAlly1EX','U7OT4aRm8sfTRRQTRHE5uA==',1772175902542,'b87f60529ee44739ba8a352f2b93090b'),(63,'{\"dev_name\":\"WALEE_1\",\"at\":1772175912469,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":false}','CITcNz8Z','Wbw8YemPGre91ShTVfao2Q==',1772175912475,'f48718f99a8d4a8798ff7d30b28b5c3a'),(64,'{\"dev_name\":\"WALEE_1\",\"at\":1772175912469,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":15}','lcZUKh7T','rcwL/E9b9Uo0AG2W25PLDg==',1772175912470,'31a6ce322bf24e4c86abed05181470d1'),(65,'{\"dev_name\":\"WALEE_1\",\"at\":1772175912469,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":61}','ZUwr1YN0','vTBXVK3cEbwq5eFOlzbxrA==',1772175912468,'d50db841a4504b138f77096a439dbe20'),(66,'{\"dev_name\":\"WALEE_1\",\"at\":1772175912469,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":56.0}','p5Lf9M8E','p6ZEEUjzt0dfoVhlBrasoQ==',1772175912472,'bdf1d9297a6e46d3b4023fd8e097af5b'),(67,'{\"dev_name\":\"WALEE_1\",\"at\":1772175922474,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":false}','BOHqXUlO','sznjl/IIB7SwYkXXgZTwDA==',1772175922485,'9d91ebab17184bc987eaeba88b464cd3'),(68,'{\"dev_name\":\"WALEE_1\",\"at\":1772175922474,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.1}','UzoLXd1z','dPw0Sbks3ANstGanuB2HYw==',1772175922482,'7659e3534dda402aa90ed8990a54dec3'),(69,'{\"dev_name\":\"WALEE_1\",\"at\":1772175922474,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":99}','GnsPbpbL','CW6NGLyccRyWVyZa4FBx5Q==',1772175922475,'e14d8adce98440269b560e9afe78b780'),(70,'{\"dev_name\":\"WALEE_1\",\"at\":1772175932479,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','f4NRrGNv','ID59kkIpgr43iaZI4bX39A==',1772175932489,'6038a57d45e845a7a9d0864a76835c29'),(71,'{\"dev_name\":\"WALEE_1\",\"at\":1772175932479,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.5}','nyxtm7I9','YCSajYvm1LKfOVXEHgjFkw==',1772175932485,'f79a6bf7860948e9a59b8b14a80f3dcb'),(72,'{\"dev_name\":\"WALEE_1\",\"at\":1772175932479,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":66}','84w7Rua3','AY7PmWPtXtzvBsscokzF6Q==',1772175932478,'38a706231ef14af3bdc32a8cfd8193b8'),(73,'{\"dev_name\":\"WALEE_1\",\"at\":1772175932479,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":56.3}','mrgjCNyb','X5qGT6ddIm6dDNxtoC3/uA==',1772175932480,'2bd6b481d77749eca1c0af1cadc37467'),(74,'{\"dev_name\":\"WALEE_1\",\"at\":1772175938521,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','a6JnJVYH','AIAd0tuStk0S8cRJJBusww==',1772175938530,'1aa2975eeba4479cb43edbf471c4d52f'),(75,'{\"dev_name\":\"WALEE_1\",\"at\":1772179130358,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','2j0kE23T','aZfr2f6emYTYcL2kL5KUMQ==',1772179130370,'cc17204a3bb5413887a242a794d7cdc9'),(76,'{\"dev_name\":\"WALEE_1\",\"at\":1772179130474,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":37.1}','JyVU9Mko','g23EcGQyiXCjv95OL5KWGA==',1772179130482,'4369e71c15024f5cb82653f4c2d16f42'),(77,'{\"dev_name\":\"WALEE_1\",\"at\":1772179130397,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','CEzo02Nf','j8LOxQmVQs6EHIRBOOqWJQ==',1772179130402,'08ef68f072c7417c8d9089dadcc84c44'),(78,'{\"dev_name\":\"WALEE_1\",\"at\":1772179130474,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','EUvgP6uZ','PIEGQF7blNAJ5WDCRJTJwg==',1772179130487,'d340e51ba9e34f08ab478bcf98fee543'),(79,'{\"dev_name\":\"WALEE_1\",\"at\":1772179130474,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":97}','qepJ9KQg','s7tFCryVMxzVTgCgQrrdag==',1772179130480,'4e8becffe0634067bcffb926c4e20e6a'),(80,'{\"dev_name\":\"WALEE_1\",\"at\":1772179140402,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":false}','ko4FPZGs','iLNlgnY/67w7crNPuCC6FA==',1772179140415,'dfa33f14a8d74f94a89e927f7ea993cf'),(81,'{\"dev_name\":\"WALEE_1\",\"at\":1772179140402,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":15}','A7xJwL6x','vEgJh5Ahh0gkOT/yXZGv2g==',1772179140408,'a450b792e71b43ff91a40033b669aa4b'),(82,'{\"dev_name\":\"WALEE_1\",\"at\":1772179140402,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.3}','Tf8zKfEI','Ku9SjAvF0VsBphbCcaZx9w==',1772179140411,'0f20e56cf24e4489a0c0da834303b1be'),(83,'{\"dev_name\":\"WALEE_1\",\"at\":1772179140402,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":67}','SZvIXUpX','Kg/DyDtjxj3IXmz7btotsg==',1772179140409,'3068a11e77c54bf39f43f36ce58d959e'),(84,'{\"dev_name\":\"WALEE_1\",\"at\":1772179150405,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":46.2}','CdAmE1WF','7JyuFeJRXHwCSDbYflNAXw==',1772179150412,'6c9d456402584904a276c8a7342f39b4'),(85,'{\"dev_name\":\"WALEE_1\",\"at\":1772179150405,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','KftgdJsh','hJ8RIDzJgrxt/pyMC12EXA==',1772179150419,'fd799d47ba614d39931c184d73231945'),(86,'{\"dev_name\":\"WALEE_1\",\"at\":1772179150405,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.3}','KnOTD8YF','hXQNn2zCgVmc4rWtFRW7RA==',1772179150414,'4a004ae683fe4179abf459d772d1691e'),(87,'{\"dev_name\":\"WALEE_1\",\"at\":1772179150405,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":70}','WbiRNhSs','c1SjMf0wOJ67yTKFBgsTfQ==',1772179150412,'dd3ca3178f2f46569d4f9eec5fc786a4'),(88,'{\"dev_name\":\"WALEE_1\",\"at\":1772179150405,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":13}','ZvSV2lXQ','cFDCqzsEKdPR2vpvrAZGuw==',1772179150413,'df356f280f394bdb9f316e667d1af6f8'),(89,'{\"dev_name\":\"WALEE_1\",\"at\":1772179160408,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":56.8}','55anihn5','NV0xEQnW1s854/JBCViqfg==',1772179160414,'3d0ca64a98e94062819c2054a29c4ff6'),(90,'{\"dev_name\":\"WALEE_1\",\"at\":1772179160408,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','IYOy4MQb','IMYGazSeJdu2tYBgRd2oIA==',1772179160422,'d7a19725aa954f11a7e659eadfc8413a'),(91,'{\"dev_name\":\"WALEE_1\",\"at\":1772179160408,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.8}','8AFcEAxO','avFvt5ZqEcZbs3VFi8ciBQ==',1772179160415,'41207628a2184c688d6a258389ba034c'),(92,'{\"dev_name\":\"WALEE_1\",\"at\":1772179160408,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":72}','5QE0RFgn','bvExTDNCmQrCgWOYmxTYsw==',1772179160415,'272f1fb42dbb424ca1e997e998c55e58'),(93,'{\"dev_name\":\"WALEE_1\",\"at\":1772179164168,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":0}','QPm787jq','3q9dTOvDDCHqUZyANoutbA==',1772179164179,'c9c0a93848f944b6a3bf16df70384401'),(94,'{\"dev_name\":\"WALEE_1\",\"at\":1772179188296,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','FCmkbQAo','dlpPwjq11dxCre4Dgjo4gA==',1772179188308,'ecbaef38cf384804875b9ce575e38879'),(95,'{\"dev_name\":\"WALEE_1\",\"at\":1772179188400,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":false}','2XJjqunK','3CF3DuKEfYgi/6dHTR4XZQ==',1772179188406,'3dd86ec4914f44d0bd2bc937f9dad514'),(96,'{\"dev_name\":\"WALEE_1\",\"at\":1772179188400,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":68}','KbVqQOp4','B8G1MucxsToBefxBtQeV3w==',1772179188406,'87677413a82b4f959248f6ff3bf86058'),(97,'{\"dev_name\":\"WALEE_1\",\"at\":1772179188400,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":37.0}','9ruQvl3C','7QukXuW1oiEtseJeDMFFjA==',1772179188408,'f937b906c4f6446b9a876c71e56490eb'),(98,'{\"dev_name\":\"WALEE_1\",\"at\":1772179188400,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":16}','kny0UWh9','a0WyCXYScPPqosOFVmbI/w==',1772179188402,'ec07a40ea335486b8b2fcef555147a10'),(99,'{\"dev_name\":\"WALEE_1\",\"at\":1772179188400,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":56.3}','aGG1Y5av','lhNWP2Xh0mmCi6Dkx9ZZag==',1772179188406,'372d55fb69e441f7a0cd138286493615'),(100,'{\"dev_name\":\"WALEE_1\",\"at\":1772179198338,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":false}','rr1r4loN','p73TSlCaCAgSlj3YgUFe6g==',1772179198336,'5bc0727192d149b4b949c396aab77856'),(101,'{\"dev_name\":\"WALEE_1\",\"at\":1772179198338,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":36.0}','1Onnlhqn','J0YNAQCO4wkEy93bpThbSg==',1772179198343,'338de63cef6e4d5e878ca1f994fa45e8'),(102,'{\"dev_name\":\"WALEE_1\",\"at\":1772179198338,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":12}','DyZ6UAwr','GZNES8SwqYShHRoXkmtCxQ==',1772179198340,'dd91c83bffba4eaab0ab62e633fe10bb'),(103,'{\"dev_name\":\"WALEE_1\",\"at\":1772179208341,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":95}','ZriJjYum','SGLleZobKygLmL639Vn7tg==',1772179208343,'fc2a4cc498ba441f8d6100c076b1174c'),(104,'{\"dev_name\":\"WALEE_1\",\"at\":1772179208341,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"breathe\",\"value\":15}','yOjgyJ2r','QjzcXqHIFLhVNUHtEamRpA==',1772179208343,'7642a24b50c74a5382f2c4342f85263d'),(105,'{\"dev_name\":\"WALEE_1\",\"at\":1772179208341,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":44.6}','h9vReeFx','PwigLOhVLXWKa8OhVfnY1g==',1772179208344,'54271112c7534865a48eb0fafedd2a09'),(106,'{\"dev_name\":\"WALEE_1\",\"at\":1772179268291,\"pid\":\"kCx33ym0Dt\",\"type\":2,\"status\":1}','BvWU42eZ','hdRpJJ5i7T6aVngEO2u9Ew==',1772179268303,'82fc031cd97d4d30ad312a04b5837dde'),(107,'{\"dev_name\":\"WALEE_1\",\"at\":1772179268325,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"online_status\",\"value\":\"simulated_online\"}','Q7sXBUKP','3uuITFl37xYpiOc92kAazQ==',1772179268331,'1ff623808b4147349f4fd44f3125a794'),(108,'{\"dev_name\":\"WALEE_1\",\"at\":1772179268397,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','NmVQBUtM','L106h7FxAAWwjvWJrZpnoQ==',1772179268409,'d9298f3617b54c2893c1912d4649fb52'),(109,'{\"dev_name\":\"WALEE_1\",\"at\":1772179278330,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"temperature\",\"value\":37.3}','2Zsf4nl9','2wEgF6e7ogbGeIBl8CZ2eQ==',1772179278338,'df13f3bbcea249bb877a10ade21c3437'),(110,'{\"dev_name\":\"WALEE_1\",\"at\":1772179288339,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":48.0}','mZMBzses','gk4jt2POseHhu5riN688NQ==',1772179288344,'02f1c6aafcef43c282bdf660d5305aa9'),(111,'{\"dev_name\":\"WALEE_1\",\"at\":1772179298345,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":80}','5IoUzfOG','eqIaw4d0HBZgRK8K16w8FA==',1772179298351,'9380e7d901c14a2eb7be3e10c65ffecf'),(112,'{\"dev_name\":\"WALEE_1\",\"at\":1772179318344,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"humidity\",\"value\":48.7}','qjXF63gD','PyP0/8OMHAVuM7EcutJ3XA==',1772179318350,'514c8ac935ef4c538db4f7df3fb3d821'),(113,'{\"dev_name\":\"WALEE_1\",\"at\":1772179318344,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"fall\",\"value\":true}','ksT5bfD8','ZYXuymAdvvETgU8j3LYc3Q==',1772179318352,'d5a4c0975bb8432e9c239715afe06f2e'),(114,'{\"dev_name\":\"WALEE_1\",\"at\":1772179318344,\"pid\":\"kCx33ym0Dt\",\"type\":1,\"ds_id\":\"rate\",\"value\":80}','oYpMcM0y','EYbEvDBKxpHfZLZTAr1jHw==',1772179318350,'0c28e0eeb2af4fa99941efcd86ff8990');
/*!40000 ALTER TABLE `device_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '事件ID，唯一且自增',
  `event_name` varchar(20) NOT NULL COMMENT '事件名称',
  `event_date` date NOT NULL COMMENT '事件日期',
  `event_time` time NOT NULL COMMENT '事件时间',
  `repeat_days` int NOT NULL COMMENT '重复天数',
  `priority` enum('low','medium','high') NOT NULL COMMENT '优先级',
  `machines` varchar(20) NOT NULL COMMENT '使用设备',
  `description` varchar(100) NOT NULL COMMENT '描述',
  `user_id` int NOT NULL COMMENT '用户ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='事件表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
INSERT INTO `event` VALUES (1,'吃药','2026-01-23','00:01:00',1,'high','00001','吃中药',9),(2,'吃药','2026-01-26','21:15:00',11,'high','00001','喝完酒吃头孢',1),(3,'遛狗','2026-01-29','00:00:00',1,'high','00001','遛狗',9),(4,'遛狗','2026-02-04','23:34:00',7,'medium','00001','遛狗，带着去拉屎',1);
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_breathe`
--

DROP TABLE IF EXISTS `sensor_breathe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_breathe` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` varchar(100) NOT NULL,
  `breathe` int NOT NULL,
  `timestamp` bigint NOT NULL,
  `message_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device_time` (`device_id`,`timestamp`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_breathe`
--

LOCK TABLES `sensor_breathe` WRITE;
/*!40000 ALTER TABLE `sensor_breathe` DISABLE KEYS */;
INSERT INTO `sensor_breathe` VALUES (1,'kCx33ym0Dt',13,1772175902542,'5c7a59f5dc8f43548ccef1eb6b26d633','2026-02-27 07:05:03'),(2,'kCx33ym0Dt',15,1772175912470,'31a6ce322bf24e4c86abed05181470d1','2026-02-27 07:05:12'),(3,'kCx33ym0Dt',15,1772179140408,'a450b792e71b43ff91a40033b669aa4b','2026-02-27 07:59:00'),(4,'kCx33ym0Dt',13,1772179150413,'df356f280f394bdb9f316e667d1af6f8','2026-02-27 07:59:10'),(5,'kCx33ym0Dt',16,1772179188402,'ec07a40ea335486b8b2fcef555147a10','2026-02-27 07:59:48'),(6,'kCx33ym0Dt',12,1772179198340,'dd91c83bffba4eaab0ab62e633fe10bb','2026-02-27 07:59:58'),(7,'kCx33ym0Dt',15,1772179208343,'7642a24b50c74a5382f2c4342f85263d','2026-02-27 08:00:08');
/*!40000 ALTER TABLE `sensor_breathe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_data`
--

DROP TABLE IF EXISTS `sensor_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_data` (
  `id` bigint NOT NULL COMMENT '时间戳作为唯一ID',
  `fall` tinyint(1) DEFAULT '0' COMMENT '跌倒状态',
  `temperature` double DEFAULT '0' COMMENT '温度',
  `humidity` double DEFAULT '0' COMMENT '湿度',
  `rate` int DEFAULT '0' COMMENT '心率',
  `breathe` int DEFAULT '0' COMMENT '呼吸频率',
  `device_id` varchar(64) DEFAULT NULL COMMENT '设备ID',
  `timestamp` bigint DEFAULT NULL COMMENT '数据时间戳',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_device_id` (`device_id`),
  KEY `idx_timestamp` (`timestamp`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='传感器数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_data`
--

LOCK TABLES `sensor_data` WRITE;
/*!40000 ALTER TABLE `sensor_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `sensor_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_fall`
--

DROP TABLE IF EXISTS `sensor_fall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_fall` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` varchar(100) NOT NULL,
  `fall` tinyint(1) NOT NULL,
  `timestamp` bigint NOT NULL,
  `message_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device_time` (`device_id`,`timestamp`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_fall`
--

LOCK TABLES `sensor_fall` WRITE;
/*!40000 ALTER TABLE `sensor_fall` DISABLE KEYS */;
INSERT INTO `sensor_fall` VALUES (1,'kCx33ym0Dt',0,1772175912475,'f48718f99a8d4a8798ff7d30b28b5c3a','2026-02-27 07:05:12'),(2,'kCx33ym0Dt',0,1772175922485,'9d91ebab17184bc987eaeba88b464cd3','2026-02-27 07:05:22'),(3,'kCx33ym0Dt',1,1772175932489,'6038a57d45e845a7a9d0864a76835c29','2026-02-27 07:05:32'),(4,'kCx33ym0Dt',1,1772179130487,'d340e51ba9e34f08ab478bcf98fee543','2026-02-27 07:58:50'),(5,'kCx33ym0Dt',0,1772179140415,'dfa33f14a8d74f94a89e927f7ea993cf','2026-02-27 07:59:00'),(6,'kCx33ym0Dt',1,1772179150419,'fd799d47ba614d39931c184d73231945','2026-02-27 07:59:10'),(7,'kCx33ym0Dt',1,1772179160422,'d7a19725aa954f11a7e659eadfc8413a','2026-02-27 07:59:20'),(8,'kCx33ym0Dt',0,1772179188406,'3dd86ec4914f44d0bd2bc937f9dad514','2026-02-27 07:59:48'),(9,'kCx33ym0Dt',0,1772179198336,'5bc0727192d149b4b949c396aab77856','2026-02-27 07:59:58'),(10,'kCx33ym0Dt',1,1772179268409,'d9298f3617b54c2893c1912d4649fb52','2026-02-27 08:01:08'),(11,'kCx33ym0Dt',1,1772179318352,'d5a4c0975bb8432e9c239715afe06f2e','2026-02-27 08:01:58');
/*!40000 ALTER TABLE `sensor_fall` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_humidity`
--

DROP TABLE IF EXISTS `sensor_humidity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_humidity` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` varchar(100) NOT NULL,
  `humidity` double NOT NULL,
  `timestamp` bigint NOT NULL,
  `message_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device_time` (`device_id`,`timestamp`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_humidity`
--

LOCK TABLES `sensor_humidity` WRITE;
/*!40000 ALTER TABLE `sensor_humidity` DISABLE KEYS */;
INSERT INTO `sensor_humidity` VALUES (1,'kCx33ym0Dt',58.5,1772175902542,'b87f60529ee44739ba8a352f2b93090b','2026-02-27 07:05:03'),(2,'kCx33ym0Dt',56,1772175912472,'bdf1d9297a6e46d3b4023fd8e097af5b','2026-02-27 07:05:12'),(3,'kCx33ym0Dt',56.3,1772175932480,'2bd6b481d77749eca1c0af1cadc37467','2026-02-27 07:05:32'),(4,'kCx33ym0Dt',46.2,1772179150412,'6c9d456402584904a276c8a7342f39b4','2026-02-27 07:59:10'),(5,'kCx33ym0Dt',56.8,1772179160414,'3d0ca64a98e94062819c2054a29c4ff6','2026-02-27 07:59:20'),(6,'kCx33ym0Dt',56.3,1772179188406,'372d55fb69e441f7a0cd138286493615','2026-02-27 07:59:48'),(7,'kCx33ym0Dt',44.6,1772179208344,'54271112c7534865a48eb0fafedd2a09','2026-02-27 08:00:08'),(8,'kCx33ym0Dt',48,1772179288344,'02f1c6aafcef43c282bdf660d5305aa9','2026-02-27 08:01:28'),(9,'kCx33ym0Dt',48.7,1772179318350,'514c8ac935ef4c538db4f7df3fb3d821','2026-02-27 08:01:58');
/*!40000 ALTER TABLE `sensor_humidity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_rate`
--

DROP TABLE IF EXISTS `sensor_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_rate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` varchar(100) NOT NULL,
  `rate` int NOT NULL,
  `timestamp` bigint NOT NULL,
  `message_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device_time` (`device_id`,`timestamp`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_rate`
--

LOCK TABLES `sensor_rate` WRITE;
/*!40000 ALTER TABLE `sensor_rate` DISABLE KEYS */;
INSERT INTO `sensor_rate` VALUES (1,'kCx33ym0Dt',77,1772175902540,'9f97459ed92045798e20cb73f4ce0d3c','2026-02-27 07:05:03'),(2,'kCx33ym0Dt',61,1772175912468,'d50db841a4504b138f77096a439dbe20','2026-02-27 07:05:12'),(3,'kCx33ym0Dt',99,1772175922475,'e14d8adce98440269b560e9afe78b780','2026-02-27 07:05:22'),(4,'kCx33ym0Dt',66,1772175932478,'38a706231ef14af3bdc32a8cfd8193b8','2026-02-27 07:05:32'),(5,'kCx33ym0Dt',97,1772179130480,'4e8becffe0634067bcffb926c4e20e6a','2026-02-27 07:58:50'),(6,'kCx33ym0Dt',67,1772179140409,'3068a11e77c54bf39f43f36ce58d959e','2026-02-27 07:59:00'),(7,'kCx33ym0Dt',70,1772179150412,'dd3ca3178f2f46569d4f9eec5fc786a4','2026-02-27 07:59:10'),(8,'kCx33ym0Dt',72,1772179160415,'272f1fb42dbb424ca1e997e998c55e58','2026-02-27 07:59:20'),(9,'kCx33ym0Dt',68,1772179188406,'87677413a82b4f959248f6ff3bf86058','2026-02-27 07:59:48'),(10,'kCx33ym0Dt',95,1772179208343,'fc2a4cc498ba441f8d6100c076b1174c','2026-02-27 08:00:08'),(11,'kCx33ym0Dt',80,1772179298351,'9380e7d901c14a2eb7be3e10c65ffecf','2026-02-27 08:01:38'),(12,'kCx33ym0Dt',80,1772179318350,'0c28e0eeb2af4fa99941efcd86ff8990','2026-02-27 08:01:58');
/*!40000 ALTER TABLE `sensor_rate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_temperature`
--

DROP TABLE IF EXISTS `sensor_temperature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_temperature` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` varchar(100) NOT NULL,
  `temperature` double NOT NULL,
  `timestamp` bigint NOT NULL,
  `message_id` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_device_time` (`device_id`,`timestamp`),
  KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_temperature`
--

LOCK TABLES `sensor_temperature` WRITE;
/*!40000 ALTER TABLE `sensor_temperature` DISABLE KEYS */;
INSERT INTO `sensor_temperature` VALUES (1,'kCx33ym0Dt',37,1772175902547,'bd2856e16c87493fb7fbd0a08d15ef0d','2026-02-27 07:05:03'),(2,'kCx33ym0Dt',36.1,1772175922482,'7659e3534dda402aa90ed8990a54dec3','2026-02-27 07:05:22'),(3,'kCx33ym0Dt',36.5,1772175932485,'f79a6bf7860948e9a59b8b14a80f3dcb','2026-02-27 07:05:32'),(4,'kCx33ym0Dt',37.1,1772179130482,'4369e71c15024f5cb82653f4c2d16f42','2026-02-27 07:58:50'),(5,'kCx33ym0Dt',36.3,1772179140411,'0f20e56cf24e4489a0c0da834303b1be','2026-02-27 07:59:00'),(6,'kCx33ym0Dt',36.3,1772179150414,'4a004ae683fe4179abf459d772d1691e','2026-02-27 07:59:10'),(7,'kCx33ym0Dt',36.8,1772179160415,'41207628a2184c688d6a258389ba034c','2026-02-27 07:59:20'),(8,'kCx33ym0Dt',37,1772179188408,'f937b906c4f6446b9a876c71e56490eb','2026-02-27 07:59:48'),(9,'kCx33ym0Dt',36,1772179198343,'338de63cef6e4d5e878ca1f994fa45e8','2026-02-27 07:59:58'),(10,'kCx33ym0Dt',37.3,1772179278338,'df13f3bbcea249bb877a10ade21c3437','2026-02-27 08:01:18');
/*!40000 ALTER TABLE `sensor_temperature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID，唯一且自增',
  `username` varchar(10) NOT NULL COMMENT '用户名',
  `phone_number` varchar(11) NOT NULL COMMENT '手机号',
  `password` varchar(32) NOT NULL COMMENT '密码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'刘华韬','18210698846','123456');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-27 16:12:13
