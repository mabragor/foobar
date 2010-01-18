alter table storage_schedule add column `duration` integer not null after begin;
update storage_schedule set duration=60 where course_id in (select id from storage_course where duration=1);
update storage_schedule set duration=90 where course_id in (select id from storage_course where duration=1.5);
