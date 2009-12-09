-- добавляем поля для учёта отмены
alter table storage_card add column `cnl_date` datetime after exp_date;
