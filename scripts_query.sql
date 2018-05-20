SET NAMES utf8mb4; 
ALTER DATABASE epaes_db CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;
select * from messages;
select * from session;
select * from chat;
select * from event_logs;
select * from messages_logs;
select * from type_messages;
select * from category_messages;

update session set user_ends_session = 1 where id_user_session = '1679689618770152' and auto_ends_session <> 1 and user_ends_session <> 1;

SET SQL_SAFE_UPDATES = 0;

select id_message, description_message, id_type_message from messages where init_message = 1;
select id_message, description_message, id_type_message from messages where message_parent = 3;
select * from session where id_user_session = '1679689618770152' and date_start_session < 
'2018-05-05 00:51:07.274990' and date_finish_session > '2018-05-05 00:51:07.274990';

select extract(hour from timediff(date_finish_session, date_start_session)) as hours,
extract(minute from timediff(date_finish_session, date_start_session)) as minutes,
extract(second from timediff(date_finish_session, date_start_session)) as seconds 
from session where id_user_session = '1679689618770152';

select sum(extract(hour from timediff(date_finish_session, date_start_session))) as hours,
sum(extract(minute from timediff(date_finish_session, date_start_session))) as minutes,
sum(extract(second from timediff(date_finish_session, date_start_session))) as seconds 
from session where id_user_session = '1679689618770152' group by id_user_session;

insert into messages (`description_message`,`id_type_message`,`id_category_message`,`init_message`,`message_parent`,`is_message_button`,`message_status`) values ('Practica con la siguiente oración: 🤓', '2', '1', '0', '16','0', '1');
insert into messages (`description_message`,`id_type_message`,`id_category_message`,`init_message`,`message_parent`,`is_message_button`,`message_status`) values ('Cuánto cuestan las boletas para la película "De Regreso al Futuro 4"?', '2', '1', '0', '16','0', '1');

select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent
inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = 12 and mr.relation_status = 1 and mch.id_type_message = 3;

select * from messages_relations;
select * from messages;
select * from category_messages;
select * from type_messages;

select m.* from messages as m inner join messages_relations as mr on m.id_message = mr.message_parent where mr.message_child in (select m.id_message from messages as m inner join messages_relations as mr on m.id_message = mr.message_parent where mr.message_child = 3) limit 1;

select m.* from messages as m inner join messages_relations as mr on m.id_message = mr.message_parent where mr.message_child in (select m.id_message from messages as m inner join messages_relations as mr on m.id_message = mr.message_parent where mr.message_child = 11) limit 1;

select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = 25 and mch.is_message_button = 1 and mr.relation_status = 1

