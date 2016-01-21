drop table if exists all_db_info;
create table all_db_info(
    id integer primary key autoincrement,
    dbdate integer not null,
    dbname string not null,
    create_time string 
);
insert into all_db_info (dbdate,dbname,create_time) values (1453046400.0,"./db/20160118-crashinfo.db","2016-01-20");
