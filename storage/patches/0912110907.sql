-- добавляем поле типа карты
alter table storage_card add column `type` varchar(1) NOT NULL after `client_id`;

-- добавляем поле с зарплатой преподавателя
alter table storage_course add column `salary` integer NOT NULL after `reg_date`;
