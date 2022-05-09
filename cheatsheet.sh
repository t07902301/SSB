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

#Use disk image from cloudlab. All postgres-related files are stored in the root directory which is copied in the image. APT cluster

psql -f "pg_schema.sql" 

show tables:
$ psql -U postgres -d dvdrental 
    OR postgres=# \c dvdrental
        You are now connected to database "dvdrental" as user "postgres". 
postgres=# \dt

create/drop database ""

dvdrental=# select count(*) from film;

STORAGE should be LARGE!

pkill -u postgres

\set path '/users/yiwei/ssb-kit/dbgen/'

# Communication between physica nodes
$ export dataDirRoot=$/home/postgres/pgxc_ctl/nodes

add gtm master gtm yiwei@apt048.apt.emulab.net 22 $dataDirRoot/gtm

# Delete 
root to delete datanode files
 ssh -v yiwei@apt045.apt.emulab.net
Host ssh -p 22 yiwei@apt045.apt.emulab.net
  ForwardAgent yes

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