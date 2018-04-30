drop table if exists entries;
create table entries (
  id integer primary key autoincrement,	
  temperature float not null,
  pressure float not null,
  humidity float not null,
  Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP not null
);
