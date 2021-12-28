import psycopg2
def connect():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="ssb",
            user="postgres",
        password="")
        return conn
    except Exception as error:
        print(error)
def delopy(replicated_table,partition):
    replicated_tbls=[]
    partition_tbls=[]
    for tbl,replicated in replicated_table.items():
        if replicated:
            replicated_tbls.append(tbl)
    for tbl,partitioned in partition.items():
        if partitioned:
            partition_tbls.append(tbl)
# conn = create_postgres_conn(config, dataset)
# content = explain_sql(sql, conn, honor_join_order, format)
