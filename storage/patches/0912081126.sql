-- новые поля
alter table storage_card change column `count` `count_sold` integer NOT NULL;
alter table storage_card add column `count_used` integer NOT NULL;
alter table storage_card add column `price` double precision NOT NULL;
