-- добавляем поля для учёта даты начала курса
alter table storage_card add column `bgn_date` datetime after reg_date;
