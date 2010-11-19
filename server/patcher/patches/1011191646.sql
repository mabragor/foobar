alter table storage_coach add column `main_style_id` integer not null;
update storage_coach set main_style_id=1;
