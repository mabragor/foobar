alter table storage_cardordinary add column `priority` integer not null after `slug`;
alter table storage_cardclub add column `priority` integer not null after `slug`;
alter table storage_cardpromo add column `priority` integer not null after `slug`;
update storage_cardordinary set priority=0;
update storage_cardclub set priority=0;
update storage_cardpromo set priority=0;
