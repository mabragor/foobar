-- разрешаем отсутствие RFID
alter table storage_client modify column `rfid_code` varchar(8) null;
