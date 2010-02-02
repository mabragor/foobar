alter table storage_schedule add column `duration` float not null after begin;
update storage_schedule set duration=1 where course_id in (select id from storage_course where duration=1);
update storage_schedule set duration=1.5 where course_id in (select id from storage_course where duration=1.5);
