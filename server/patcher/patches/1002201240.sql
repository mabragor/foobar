alter table storage_team add column `coach_id` integer not null after id;
update storage_team a join storage_team_coach b on a.id=b.team_id set a.coach_id=b.coach_id;
drop table storage_team_coach;
