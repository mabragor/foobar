alter table storage_card change column `course_id` `team_id` integer not null;
alter table storage_schedule change column `course_id` `team_id` integer;
