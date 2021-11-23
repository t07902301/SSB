import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        database="ssb",
        user="postgres",
    password="")
except Exception as error:
    print(error)
# conn = create_postgres_conn(config, dataset)
# content = explain_sql(sql, conn, honor_join_order, format)