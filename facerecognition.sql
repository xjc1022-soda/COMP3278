-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Feb 17, 2020 at 09:41 PM
-- Server version: 5.7.28-0ubuntu0.18.04.4
-- PHP Version: 7.2.24-0ubuntu0.18.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `facerecognition`
--

-- --------------------------------------------------------

--
-- Table structure for table `Student`
--
DROP DATABASE IF EXISTS `facerecognition`;
CREATE DATABASE `facerecognition`;
USE `facerecognition`;

# Create TABLE 'Student'
CREATE TABLE `Student` (
  `student_id` int NOT NULL PRIMARY KEY,
  `name` varchar(50) NOT NULL,
  `login_time` time NOT NULL,
  `login_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `Student` WRITE;
/*!40000 ALTER TABLE `Student` DISABLE KEYS */;
INSERT INTO `Student` VALUES (1, "JACK", NOW(), '2021-01-20');
/*!40000 ALTER TABLE `Student` ENABLE KEYS */;
UNLOCK TABLES;

# Create TABLE 'Classroom'
CREATE TABLE `Classroom` (
  `classroom_id` int NOT NULL PRIMARY KEY,
  `address` varchar(50) NOT NULL,
  `login_time` time NOT NULL,
  `login_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

# Create TABLE 'Course'
CREATE TABLE `Course` (
  `course_id` varchar(50) NOT NULL PRIMARY KEY,
  `course_information` varchar(50) NOT NULL,
  `classroom_id` int NOT NULL,
  `message` varchar(50) NOT NULL,
  `zoom_link` varchar(50) NOT NULL,
  `materials_link` varchar(50) NOT NULL,
  FOREIGN KEY (`classroom_id`) REFERENCES `Classroom` (`classroom_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

# Create other TABLE...
CREATE TABLE `Attend` (
  `student_id` int NOT NULL,
  `course_id` varchar(50) NOT NULL,
  FOREIGN KEY (`student_id`) REFERENCES `Student` (`student_id`),
  FOREIGN KEY (`course_id`) REFERENCES `Course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
LOCK TABLES `Attend` WRITE;
#INSERT INTO `Attend` (`student_id`,`course_id`) VALUES ('2', '1');

CREATE TABLE `StartDate` (
  `course_id` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  FOREIGN KEY (`course_id`) REFERENCES `Course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
#INSERT INTO `Classroom` (`classroom_id`,`address`) VALUES ('1', 'XXX');
#INSERT INTO `Course` (`course_id`, `course_information`, `classroom_id`, `message`,`zoom_link`,`materials_link`) VALUES ('1', 'XXX', '1', 'XXX', 'XXX', 'YYY');
#INSERT INTO `Attend` (`student_id`,`course_id`) VALUES ('2', '1');
#INSERT INTO `StartDate` (`course_id`,`date`,`time`) VALUES ('1', '2022-11-05', '03:30:00');