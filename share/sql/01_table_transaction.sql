CREATE TABLE IF NOT EXISTS `transaction` (
  `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `service_id` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_id` int(11) UNSIGNED NOT NULL,
  `type` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(20, 2) NOT NULL,
  `currency` char(3) NOT NULL,
  `country` varchar(30) NOT NULL,
  `backend` varchar(30) NOT NULL,
  `callback` varchar(255) NOT NULL,
  `extra` varchar(2048) DEFAULT NULL,
  `status` varchar(30) NOT NULL DEFAULT 'NEW',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
