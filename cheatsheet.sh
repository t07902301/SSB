sudo -i

psql -f "pg_schema.sql" 

show tables:
$ psql -U postgres -d dvdrental 
    OR postgres=# \c dvdrental
        You are now connected to database "dvdrental" as user "postgres". 
postgres=# \dt

create/drop database ""

dvdrental=# select count(*) from film;

STORAGE should be LARGE!

wget https://www.postgres-xl.org/downloads/postgres-xl-10r1.1.tar.gz
tar -xf postgres-xl-10r1.1.tar.gz
apt update
sudo apt install libreadline-dev
./configure
make
  (All of PostgreSQL successfully made. Ready to install.)
(root)
make install
PATH=/usr/local/pgsql/bin:$PATH
export PATH
. ~/.bashrc
sudo adduser postgres --disabled-password

pkill -u postgres
/usr/local/pgsql/bin/psql
ps -elf | grep postgres
sudo systemctl start postgresql
sudo systemctl status postgresql

psql p1

/usr/local/pgsql/bin/pgxc_ctl

\set path '/users/yiwei/ssb-kit/dbgen/'

$ export dataDirRoot=$/home/postgres/pgxc_ctl/nodes

add gtm master gtm yiwei@apt048.apt.emulab.net 22 $dataDirRoot/gtm

psql -d p -c "EXPLAIN analyze $( cat q1-1.sql )"
psql -d p -c "EXPLAIN analyze $( cat q2-1.sql )"
psql -d p -c "EXPLAIN analyze $( cat q3-1.sql )"
psql -d p -c "EXPLAIN analyze $( cat q4-1.sql )"

mkdir /usr/local/pgsql/data_datanode_3
chown postgres /usr/local/pgsql/data_datanode_3
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data_datanode_3 \
  --nodename datanode_3
/usr/local/pgsql/bin/postgres --datanode -p 40001 -c pooler_port=40011 \
  -D /usr/local/pgsql/data_datanode_3 >logfile 2>&1 &
psql -c "CREATE NODE datanode_3 \
  WITH (TYPE = 'datanode', PORT = 40001)" postgres

psql -c "DROP NODE datanode_3" postgres


psql -c "EXECUTE DIRECT ON (datanode_3) \
  'ALTER NODE datanode_3 WITH (TYPE = ''datanode'', PORT = 40001)'" postgres

psql -c "EXECUTE DIRECT ON (datanode_3) \
  'ALTER NODE datanode_3 WITH (TYPE = ''datanode'', PORT = 40001)'" postgres
psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE datanode_1 WITH (TYPE = ''datanode'', PORT = 15432)'" postgres
psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE datanode_2 WITH (TYPE = ''datanode'', PORT = 15433)'" postgres
psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE coord1 WITH (TYPE = ''coordinator'', PORT = 5432)'" postgres

#reload
psql -c "SELECT pgxc_pool_reload()" postgres
psql -c "EXECUTE DIRECT ON (datanode_1) \
  'SELECT pgxc_pool_reload()'" postgres
psql -c "EXECUTE DIRECT ON (datanode_2) \
  'SELECT pgxc_pool_reload()'" postgres
psql -c "EXECUTE DIRECT ON (datanode_3) \
  'SELECT pgxc_pool_reload()'" postgres
psql -c "EXECUTE DIRECT ON (datanode_4) \
  'SELECT pgxc_pool_reload()'" postgres

# Delete 
root to delete datanode files
 ssh -v yiwei@apt045.apt.emulab.net
Host ssh -p 22 yiwei@apt045.apt.emulab.net
  ForwardAgent yes
#Select
SELECT * FROM pgxc_node;
SELECT xc_node_id, count(*) FROM supplier GROUP BY xc_node_id;

#alter
ALTER TABLE dim_date DISTRIBUTE BY REPLICATION;
ALTER TABLE part DISTRIBUTE BY REPLICATION;

ALTER TABLE lineorder DISTRIBUTE BY REPLICATION;
ALTER TABLE supplier DISTRIBUTE BY REPLICATION;
ALTER TABLE supplier DISTRIBUTE BY HASH(s_name);

ALTER TABLE customer DELETE NODE (datanode_2);
ALTER TABLE supplier ADD NODE (datanode_2);

ALTER TABLE part DELETE NODE (datanode_2);
ALTER TABLE part DELETE NODE (datanode_3);
ALTER TABLE part DELETE NODE (datanode_4);

ALTER TABLE supplier ADD NODE (datanode_2);
ALTER TABLE supplier ADD NODE (datanode_3);
ALTER TABLE supplier ADD NODE (datanode_4);

ALTER TABLE supplier DISTRIBUTE BY HASH(s_address);

SELECT xc_node_id, count(*) FROM customer GROUP BY xc_node_id;
ALTER USER postgres WITH PASSWORD '123';


{'customer': 0, 'dim_date': 1, 'lineorder': 1, 'part': 0, 'supplier': 0}
{'customer': 'c_custkey', 'part': 'p_partkey', 'supplier': 's_address'}