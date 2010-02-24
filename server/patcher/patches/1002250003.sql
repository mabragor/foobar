alter table storage_team add column `price_group_id` integer not null after `id`;
insert into storage_pricegroup (id, title) values (1, 'Стандартная');
update storage_team set price_group_id=1;
