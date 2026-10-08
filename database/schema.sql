CREATE TABLE f_f4c5a58c__study_sessions (
  id CHAR(36) NOT NULL,
  completed_at TIMESTAMP NOT NULL,
  duration_minutes INT NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE f_7a9d9848__completed_sessions (
  id CHAR(36) NOT NULL,
  completed_at TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;


-- No database tables are required for feature: capability_reset_timer_e8a699f5


CREATE TABLE `f_a5aab8dc__timer_session` (
  `id` CHAR(36) NOT NULL,
  `remaining_seconds` INT NOT NULL,
  `is_running` BOOLEAN NOT NULL,
  `started_at` TIMESTAMP NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CHECK (`remaining_seconds` >= 0 AND `remaining_seconds` <= 1500)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- No database tables are required for feature: capability_timer_display_c4871171


-- No database tables are required for feature: capability_session_complete_message_a549a4b8


-- No database tables are required for feature: capability_session_completion_sound_5b6b2529


-- No database tables are required for feature: capability_pause_timer_520df3b4


CREATE TABLE `f_145f595e__daily_session_state` (
  `id` CHAR(36) NOT NULL,
  `session_count` INT UNSIGNED NOT NULL,
  `current_date` DATE NOT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- No database tables are required for feature: capability_no_tutorial_on_launch_a952579e


-- No database tables are required for feature: capability_clean_visual_design_7f205967


CREATE TABLE `f_f65ac826__timer_state` (
  `id` CHAR(36) NOT NULL,
  `remaining_seconds` INT NOT NULL,
  `paused_at` TIMESTAMP NOT NULL,
  `is_paused` BOOLEAN NOT NULL,
  `updated_at` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;