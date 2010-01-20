alter table storage_schedule add column `end` datetime not null after begin;
update storage_schedule set end=addtime(begin, sec_to_time(duration * 3600));
