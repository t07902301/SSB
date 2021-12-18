mkdir /usr/local/pgsql/data_coord1
mkdir /usr/local/pgsql/data_datanode_1
mkdir /usr/local/pgsql/data_datanode_2
mkdir /usr/local/pgsql/data_datanode_3
mkdir /usr/local/pgsql/data_datanode_4
mkdir /usr/local/pgsql/data_gtm
chown postgres /usr/local/pgsql/data_coord1
chown postgres /usr/local/pgsql/data_datanode_1
chown postgres /usr/local/pgsql/data_datanode_2
chown postgres /usr/local/pgsql/data_datanode_3
chown postgres /usr/local/pgsql/data_datanode_4
chown postgres /usr/local/pgsql/data_gtm

/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data_coord1 \
  --nodename coord1
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data_datanode_1 \
  --nodename datanode_1
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data_datanode_2 \
  --nodename datanode_2
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data_datanode_3 \
  --nodename datanode_3
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data_datanode_4 \
  --nodename datanode_4

/usr/local/pgsql/bin/initgtm -D /usr/local/pgsql/data_gtm -Z gtm
/usr/local/pgsql/bin/gtm -D /usr/local/pgsql/data_gtm >logfile 2>&1 &

/usr/local/pgsql/bin/postgres --datanode -p 15432 -c pooler_port=40101 \
  -D /usr/local/pgsql/data_datanode_1 >logfile 2>&1 &
/usr/local/pgsql/bin/postgres --datanode -p 15433 -c pooler_port=40102 \
  -D /usr/local/pgsql/data_datanode_2 >logfile 2>&1 &
/usr/local/pgsql/bin/postgres --datanode -p 30001  -c pooler_port=30011  \
  -D /usr/local/pgsql/data_datanode_3 >logfile 2>&1 &
/usr/local/pgsql/bin/postgres --datanode -p 30002 -c pooler_port=30012 \
  -D /usr/local/pgsql/data_datanode_4 >logfile 2>&1 &
/usr/local/pgsql/bin/postgres --coordinator -c pooler_port=40100 \
  -D /usr/local/pgsql/data_coord1 >logfile 2>&1 &

/usr/local/pgsql/bin/psql -c "ALTER NODE coord1 \
  WITH (TYPE = 'coordinator', PORT = 5432)" postgres
/usr/local/pgsql/bin/psql -c "CREATE NODE datanode_1 \
  WITH (TYPE = 'datanode', PORT = 15432)" postgres
/usr/local/pgsql/bin/psql -c "CREATE NODE datanode_2 \
  WITH (TYPE = 'datanode', PORT = 15433)" postgres
/usr/local/pgsql/bin/psql -c "CREATE NODE datanode_3 \
  WITH (TYPE = 'datanode', PORT = 30001)" postgres
/usr/local/pgsql/bin/psql -c "CREATE NODE datanode_4 \
  WITH (TYPE = 'datanode', PORT = 30002)" postgres

/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_1) \
  'ALTER NODE datanode_1 WITH (TYPE = ''datanode'', PORT = 15432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_1) \
  'CREATE NODE datanode_2 WITH (TYPE = ''datanode'', PORT = 15433)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_1) \
  'CREATE NODE coord1 WITH (TYPE = ''coordinator'', PORT = 5432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_1) \
  'CREATE NODE datanode_3 WITH (TYPE = ''datanode'', PORT = 30001)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_1) \
  'CREATE NODE datanode_4 WITH (TYPE = ''datanode'', PORT = 30002)'" postgres

/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_2) \
  'ALTER NODE datanode_2 WITH (TYPE = ''datanode'', PORT = 15433)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_2) \
  'CREATE NODE datanode_1 WITH (TYPE = ''datanode'', PORT = 15432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_2) \
  'CREATE NODE coord1 WITH (TYPE = ''coordinator'', PORT = 5432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_2) \
  'CREATE NODE datanode_3 WITH (TYPE = ''datanode'', PORT = 30001)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_2) \
  'CREATE NODE datanode_4 WITH (TYPE = ''datanode'', PORT = 30002)'" postgres

/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_3) \
  'ALTER NODE datanode_3 WITH (TYPE = ''datanode'', PORT = 30001)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE datanode_2 WITH (TYPE = ''datanode'', PORT = 15433)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE coord1 WITH (TYPE = ''coordinator'', PORT = 5432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE datanode_1 WITH (TYPE = ''datanode'', PORT = 15432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_3) \
  'CREATE NODE datanode_4 WITH (TYPE = ''datanode'', PORT = 30002)'" postgres

/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_4) \
  'ALTER NODE datanode_4 WITH (TYPE = ''datanode'', PORT = 30002)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_4) \
  'CREATE NODE datanode_2 WITH (TYPE = ''datanode'', PORT = 15433)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_4) \
  'CREATE NODE coord1 WITH (TYPE = ''coordinator'', PORT = 5432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_4) \
  'CREATE NODE datanode_1 WITH (TYPE = ''datanode'', PORT = 15432)'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_4) \
  'CREATE NODE datanode_3 WITH (TYPE = ''datanode'', PORT = 30001)'" postgres

/usr/local/pgsql/bin/psql -c "SELECT pgxc_pool_reload()" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_1) \
  'SELECT pgxc_pool_reload()'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_2) \
  'SELECT pgxc_pool_reload()'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_3) \
  'SELECT pgxc_pool_reload()'" postgres
/usr/local/pgsql/bin/psql -c "EXECUTE DIRECT ON (datanode_4) \
  'SELECT pgxc_pool_reload()'" postgres