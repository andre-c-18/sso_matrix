-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.32-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.15.0.7171
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table sso_db_test.access_matrix
CREATE TABLE IF NOT EXISTS `access_matrix` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) NOT NULL,
  `app_id` int(11) NOT NULL DEFAULT 0,
  `standard_access` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`standard_access`)),
  `right_config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`right_config`)),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_role_app` (`role_id`,`app_id`) USING BTREE,
  KEY `app_id` (`app_id`) USING BTREE,
  CONSTRAINT `access_matrix_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `access_matrix_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `applications` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table sso_db_test.access_matrix: ~8 rows (approximately)
INSERT INTO `access_matrix` (`id`, `role_id`, `app_id`, `standard_access`, `right_config`, `updated_at`) VALUES
	(9, 1, 2, '["view", "add", "edit", "export", "approve", "upload", "delete"]', '{"paths": []}', '2026-04-27 07:46:07'),
	(10, 2, 2, '["view", "add", "edit", "export", "approve", "upload", "delete"]', '{"paths": []}', '2026-04-27 07:46:07'),
	(11, 3, 2, '["view", "add", "edit", "export", "approve", "upload"]', '{"paths": []}', '2026-04-27 07:46:07'),
	(12, 4, 2, '["view", "add", "edit", "approve"]', '{"paths": []}', '2026-04-27 07:46:07'),
	(13, 1, 1, '["view", "add", "edit", "export", "approve", "upload", "delete"]', '{"paths": []}', '2026-04-28 01:07:45'),
	(14, 2, 1, '["view", "add", "edit", "export", "approve", "upload", "delete"]', '{"paths": []}', '2026-04-28 01:07:45'),
	(15, 3, 1, '["view", "add", "edit", "export", "approve", "upload"]', '{"paths": []}', '2026-04-28 01:07:45'),
	(16, 4, 1, '["view", "edit", "export", "approve"]', '{"paths": []}', '2026-04-28 01:44:12');

-- Dumping structure for table sso_db_test.applications
CREATE TABLE IF NOT EXISTS `applications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` varchar(100) NOT NULL,
  `app_secret` varchar(255) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `callback_url` varchar(500) NOT NULL,
  `allowed_origins` text DEFAULT NULL,
  `auto_redirect` tinyint(1) DEFAULT 0,
  `is_active` tinyint(1) DEFAULT 1,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_id` (`app_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `applications_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table sso_db_test.applications: ~0 rows (approximately)
INSERT INTO `applications` (`id`, `app_id`, `app_secret`, `app_name`, `description`, `callback_url`, `allowed_origins`, `auto_redirect`, `is_active`, `created_by`, `created_at`, `updated_at`) VALUES
	(1, 'portal_os_test_6c82e633', 'LSvCKY5dz1K2D9WxaVu0MUXWTZBSLe3jaxPVVRopBr4', 'Portal OS test', 'test', 'http://172.16.2.141:5003/auth/callback', '', 1, 1, 1, '2026-04-20 08:50:00', '2026-05-08 06:05:57'),
	(2, 'm-account_test_c7e45587', 'S9EBweGbxsVEeEhcFm_M0E6_COUyIjJ2g7A5eXmR-90', 'm-account test', 'test access right role', 'http://172.16.2.141/m-account/auth/callback', 'http://172.16.2.141', 1, 1, 1, '2026-04-27 06:42:31', '2026-05-08 06:05:46');

-- Dumping structure for table sso_db_test.audit_logs
CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `app_id` varchar(100) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `detail` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_audit_logs_user` (`user_id`),
  KEY `idx_audit_logs_created` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table sso_db_test.audit_logs: ~94 rows (approximately)
INSERT INTO `audit_logs` (`id`, `user_id`, `app_id`, `action`, `detail`, `ip_address`, `created_at`) VALUES
	(1, 1, NULL, 'USER_CREATED', 'username=user', '127.0.0.1', '2026-04-20 08:47:01'),
	(2, 1, NULL, 'APP_CREATED', 'app_id=portal_os_test_6c82e633', '127.0.0.1', '2026-04-20 08:50:00'),
	(3, 1, NULL, 'USER_CREATED', 'username=manager', '127.0.0.1', '2026-04-20 08:56:09'),
	(4, 1, NULL, 'USER_TOGGLE', 'user_id=2,active=0', '127.0.0.1', '2026-04-20 08:56:18'),
	(5, 1, NULL, 'USER_UPDATED', 'user_id=2', '127.0.0.1', '2026-04-20 08:56:26'),
	(6, 1, NULL, 'USER_CREATED', 'username=admin', '127.0.0.1', '2026-04-20 08:56:47'),
	(7, 1, NULL, 'ADMIN_RESET_PASSWORD', 'user_id=1', '127.0.0.1', '2026-04-27 06:41:06'),
	(8, 1, NULL, 'APP_CREATED', 'app_id=m-account_test_c7e45587', '127.0.0.1', '2026-04-27 06:42:31'),
	(9, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-27 06:45:05'),
	(10, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-27 07:41:36'),
	(11, 1, NULL, 'ACCESS_MATRIX_SAVED', 'app=m-account_test_c7e45587', '127.0.0.1', '2026-04-27 07:43:24'),
	(12, 1, NULL, 'ACCESS_MATRIX_SAVED', 'app=m-account_test_c7e45587', '127.0.0.1', '2026-04-27 07:46:07'),
	(13, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=users', '127.0.0.1', '2026-04-27 08:31:45'),
	(14, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=users', '127.0.0.1', '2026-04-27 08:31:54'),
	(15, 1, NULL, 'ADMIN_RESET_PASSWORD', 'user_id=2', '127.0.0.1', '2026-04-27 08:32:10'),
	(16, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=users', '127.0.0.1', '2026-04-27 08:32:16'),
	(17, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=users', '127.0.0.1', '2026-04-27 08:32:22'),
	(18, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-27 08:32:37'),
	(19, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-27 08:36:31'),
	(20, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-27 08:40:50'),
	(21, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=user', '127.0.0.1', '2026-04-27 08:41:15'),
	(22, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-27 08:41:19'),
	(23, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-27 09:16:40'),
	(24, 1, NULL, 'ACCESS_MATRIX_SAVED', 'app=portal_os_test_6c82e633', '127.0.0.1', '2026-04-28 01:07:45'),
	(25, NULL, 'portal_os_test_6c82e633', 'LOGIN_FAILED', 'username=superadmin', '127.0.0.1', '2026-04-28 01:11:52'),
	(26, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:11:56'),
	(27, 4, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:18:45'),
	(28, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:21:55'),
	(29, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:24:45'),
	(30, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:29:48'),
	(31, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:30:29'),
	(32, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:34:01'),
	(33, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 01:41:28'),
	(34, 1, NULL, 'ACCESS_MATRIX_SAVED', 'app=portal_os_test_6c82e633', '127.0.0.1', '2026-04-28 01:44:12'),
	(35, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 01:44:42'),
	(36, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 01:46:00'),
	(37, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=user', '127.0.0.1', '2026-04-28 02:02:21'),
	(38, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 02:02:27'),
	(39, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 02:03:27'),
	(40, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 02:13:33'),
	(41, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 02:36:27'),
	(42, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 02:45:15'),
	(43, 2, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'edit\', \'export\', \'approve\']', '127.0.0.1', '2026-04-28 02:48:12'),
	(44, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-28 04:01:41'),
	(45, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 04:08:01'),
	(46, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 04:11:21'),
	(47, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 04:25:14'),
	(48, 1, NULL, 'USER_CREATED', 'username=user2', '127.0.0.1', '2026-04-28 07:02:58'),
	(49, 5, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 07:04:00'),
	(50, 5, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 07:11:02'),
	(51, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-28 07:11:42'),
	(52, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-29 01:16:06'),
	(53, 1, NULL, 'ADMIN_LOGIN', NULL, '127.0.0.1', '2026-04-29 03:51:55'),
	(54, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-29 03:52:52'),
	(55, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-29 06:29:30'),
	(56, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-30 01:08:35'),
	(57, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-30 07:16:25'),
	(58, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-30 07:29:22'),
	(59, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-30 07:30:01'),
	(60, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-04-30 08:16:26'),
	(61, 1, NULL, 'ADMIN_LOGIN', NULL, '127.0.0.1', '2026-04-30 08:17:08'),
	(62, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-04-30 08:23:33'),
	(63, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-04 02:23:23'),
	(64, 2, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'approve\']', '127.0.0.1', '2026-05-04 06:50:09'),
	(65, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 01:19:48'),
	(66, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 01:40:33'),
	(67, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 02:40:52'),
	(68, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 02:49:25'),
	(69, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 04:04:00'),
	(70, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 06:26:48'),
	(71, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 07:31:11'),
	(72, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-05 08:43:03'),
	(73, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-06 01:18:59'),
	(74, 4, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-06 02:44:11'),
	(75, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-06 03:04:05'),
	(76, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-06 03:48:41'),
	(77, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-06 06:11:29'),
	(78, 1, NULL, 'ADMIN_LOGIN', NULL, '127.0.0.1', '2026-05-07 01:02:07'),
	(79, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-07 01:03:54'),
	(80, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-07 01:29:50'),
	(81, 1, 'portal_os_test_6c82e633', 'LOGIN_SUCCESS', 'app=portal_os_test_6c82e633 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-07 06:17:38'),
	(82, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-07 07:16:08'),
	(83, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '127.0.0.1', '2026-05-08 01:10:56'),
	(84, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-08 05:58:26'),
	(85, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-08 06:03:57'),
	(86, 1, NULL, 'ADMIN_LOGIN', NULL, '172.16.2.141', '2026-05-08 06:04:28'),
	(87, 1, NULL, 'APP_UPDATED', 'app_id=m-account_test_c7e45587', '172.16.2.141', '2026-05-08 06:05:46'),
	(88, 1, NULL, 'APP_UPDATED', 'app_id=portal_os_test_6c82e633', '172.16.2.141', '2026-05-08 06:05:57'),
	(89, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-08 06:06:09'),
	(90, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-08 07:25:36'),
	(91, NULL, 'm-account_test_c7e45587', 'LOGIN_FAILED', 'username=superadmin', '172.16.2.141', '2026-05-08 07:46:54'),
	(92, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-08 07:47:04'),
	(93, 1, NULL, 'ADMIN_LOGIN', NULL, '172.16.2.141', '2026-05-11 03:53:26'),
	(94, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-11 03:54:56'),
	(95, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-11 07:17:27'),
	(96, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-11 07:54:32'),
	(97, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-11 07:55:12'),
	(98, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.185', '2026-05-12 01:54:39'),
	(99, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.185', '2026-05-12 01:54:52'),
	(100, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.185', '2026-05-12 08:02:59'),
	(101, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.185', '2026-05-12 09:03:30'),
	(102, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.185', '2026-05-12 09:10:57'),
	(103, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.2.141', '2026-05-12 09:17:10'),
	(104, 1, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.131', '2026-05-13 03:20:15'),
	(105, 4, 'm-account_test_c7e45587', 'LOGIN_SUCCESS', 'app=m-account_test_c7e45587 access=[\'view\', \'add\', \'edit\', \'export\', \'approve\', \'upload\', \'delete\']', '172.16.253.131', '2026-05-13 03:43:52'),
	(106, 1, NULL, 'ADMIN_LOGIN', NULL, '127.0.0.1', '2026-05-13 07:56:34');

-- Dumping structure for table sso_db_test.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table sso_db_test.roles: ~4 rows (approximately)
INSERT INTO `roles` (`id`, `name`, `description`, `created_at`) VALUES
	(1, 'superadmin', 'Super Administrator dengan akses penuh', '2026-04-20 08:35:32'),
	(2, 'admin', 'Administrator dengan akses manajemen', '2026-04-20 08:35:32'),
	(3, 'manager', 'Manager dengan akses terbatas', '2026-04-20 08:35:32'),
	(4, 'user', 'Pengguna biasa', '2026-04-20 08:35:32');

-- Dumping structure for table sso_db_test.user_access_overrides
CREATE TABLE IF NOT EXISTS `user_access_overrides` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `app_id` int(11) NOT NULL DEFAULT 0,
  `standard_access` varchar(255) DEFAULT NULL,
  `right_config` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_user` (`user_id`),
  KEY `FK_user_access_overrides_applications` (`app_id`),
  CONSTRAINT `FK_user_access_overrides_applications` FOREIGN KEY (`app_id`) REFERENCES `applications` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table sso_db_test.user_access_overrides: ~2 rows (approximately)
INSERT INTO `user_access_overrides` (`id`, `user_id`, `app_id`, `standard_access`, `right_config`, `updated_at`) VALUES
	(1, 2, 2, '["view", "add", "edit", "export", "approve"]', '{"paths": [], "warehouse": 1, "can_sell": true}', '2026-04-27 08:31:08'),
	(4, 5, 2, '["view", "add", "edit", "export", "approve"]', '{"paths": [], "can_buy": true}', '2026-04-28 07:03:41');

-- Dumping structure for table sso_db_test.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `role_id` int(11) NOT NULL DEFAULT 4,
  `is_active` tinyint(1) DEFAULT 1,
  `is_email_verified` tinyint(1) DEFAULT 0,
  `avatar_url` varchar(500) DEFAULT NULL,
  `last_login` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for table sso_db_test.users: ~5 rows (approximately)
INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `full_name`, `role_id`, `is_active`, `is_email_verified`, `avatar_url`, `last_login`, `created_at`, `updated_at`) VALUES
	(1, 'superadmin', 'superadmin@sso.local', '$2b$12$4JpqfqhweJqy8DFqaZh3BOxlqEa.75WDx0.KpBH8gpv0yHGp.vqBi', 'Super Administrator', 1, 1, 1, NULL, '2026-05-13 07:56:34', '2026-04-20 08:35:32', '2026-05-13 07:56:34'),
	(2, 'user', 'test@test', '$2b$12$JWUMTfxWR5Fe/.yeyYd71.Cprf0pR879bnMw4vBXulewXdz/L/Uvi', 'user', 4, 1, 1, NULL, '2026-05-04 06:50:09', '2026-04-20 08:47:01', '2026-05-04 06:50:09'),
	(3, 'manager', 'manager@manager', '$2b$12$ipqAaTNTgh/beNsBUCwjHeViiR1dLdjhsPzA8krgvR69./h5QCj2W', 'manager', 3, 1, 1, NULL, NULL, '2026-04-20 08:56:09', '2026-04-20 08:56:09'),
	(4, 'admin', 'admin@admin', '$2b$12$ZQP2mpx11Gy348rWdfQ5Z.DBHGmMevGavJbkdTG1BqLsFJxZ./UiK', 'admin', 2, 1, 1, NULL, '2026-05-13 03:43:52', '2026-04-20 08:56:47', '2026-05-13 03:43:52'),
	(5, 'user2', 'user@user', '$2b$12$yRZh64sHH0veEsJrp7bmZO85KY7MKhtsHRo0XpOnwIw/d/XzKR0RC', 'user2', 4, 1, 1, NULL, '2026-04-28 07:11:02', '2026-04-28 07:02:58', '2026-04-28 07:11:02');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
