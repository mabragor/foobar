-- добавляем ссылку на модель аренды
alter table storage_schedule modify column `course_id` integer null;
alter table storage_schedule add column `rent_id` integer null after course_id;
