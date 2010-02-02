ALTER TABLE storage_action DROP COLUMN change_id, DROP COLUMN status;
ALTER TABLE storage_schedule ADD COLUMN `change_id` int(11),
ADD COLUMN `status` varchar(1),
ADD KEY `storage_action_change_id` (`change_id`);