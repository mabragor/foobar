-- добавить поле цены в таблицу с курсами
alter table storage_course add column `count` integer NOT NULL after `duration`;
alter table storage_course add column `price` double precision NOT NULL after `count`;
