-- MySQL dump 10.13  Distrib 5.5.49, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: oh_hell
-- ------------------------------------------------------
-- Server version	5.5.49-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `oh_hell`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `oh_hell` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `oh_hell`;

--
-- Table structure for table `bid`
--

DROP TABLE IF EXISTS `bid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bid` (
  `bid_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `bid` int(10) unsigned NOT NULL DEFAULT '0',
  `deal_id` int(10) unsigned NOT NULL DEFAULT '0',
  `player_id` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`bid_id`)
) ENGINE=MyISAM AUTO_INCREMENT=32394 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deal`
--

DROP TABLE IF EXISTS `deal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deal` (
  `deal_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `game_id` int(10) unsigned NOT NULL DEFAULT '0',
  `deal` int(10) unsigned NOT NULL DEFAULT '0',
  `num_cards` int(10) unsigned NOT NULL DEFAULT '0',
  `dealer_id` int(10) unsigned NOT NULL DEFAULT '0',
  `trump` int(11) DEFAULT NULL,
  PRIMARY KEY (`deal_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10740 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `game`
--

DROP TABLE IF EXISTS `game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game` (
  `game_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `time` datetime DEFAULT NULL,
  `winner_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`game_id`)
) ENGINE=MyISAM AUTO_INCREMENT=512 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `game_players`
--

DROP TABLE IF EXISTS `game_players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `game_players` (
  `game_id` int(10) unsigned NOT NULL DEFAULT '0',
  `player_id` int(10) unsigned NOT NULL DEFAULT '0',
  `game_order` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`game_id`,`player_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player` (
  `player_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `last_name` varchar(30) NOT NULL DEFAULT '',
  `first_name` varchar(20) NOT NULL DEFAULT '',
  PRIMARY KEY (`player_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trick`
--

DROP TABLE IF EXISTS `trick`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trick` (
  `trick_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `trick_num` int(10) unsigned NOT NULL DEFAULT '0',
  `winner_id` int(10) unsigned NOT NULL DEFAULT '0',
  `deal_id` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`trick_id`)
) ENGINE=MyISAM AUTO_INCREMENT=56730 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trick_cards`
--

DROP TABLE IF EXISTS `trick_cards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trick_cards` (
  `trick_id` int(10) unsigned NOT NULL DEFAULT '0',
  `player_id` int(10) unsigned NOT NULL DEFAULT '0',
  `card_num` int(10) unsigned NOT NULL DEFAULT '0',
  `card` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`trick_id`,`player_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-04-23 19:47:36
