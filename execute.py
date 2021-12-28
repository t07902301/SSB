import psycopg2,os
import numpy as np
import argparse
def connect():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="p",
            user="postgres",
        password="123")
        return conn
    except Exception as error:
        print(error)
def execute(conn,run_cnt):
    sql_base_path='queries/'
    cursor = conn.cursor()
    execution_time=[]
    for root, dirs, files in os.walk(sql_base_path):
        for sql in files:
            sql_content=open(os.path.join(sql_base_path,sql),'r').read()
            execution_per_run=[]
            # print(type(sql))
            # cursor.execute('explain (ANALYZE TRUE,FORMAT json ) {}'.format(sql_content))
            for i in range(run_cnt):
                cursor.execute('explain (ANALYZE) {}'.format(sql_content))
                results = cursor.fetchall()
                execution_per_run.append(float(results[-1][0].split(' ')[2]))
            # execution_time.append(float(results[0][0][0][-1][0].split(' ')[2]))
            execution_time.append(np.average(np.array(execution_per_run)))
            print('{} executed'.format(sql))
    total_time=np.sum(np.array(execution_time))/1000
    return total_time 
def create_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument('--epochs', type=int, nargs='?', const=True, default=1)
    return parse

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args() 
    # print(args)   
    conn=connect()
    # print(type(execute(conn)))
    # execute(conn)
    result=execute(conn,args.epochs)
    print("{}s".format(result))
    # print(type(result[0]))            
    # print(result[-1][0].split(' '))
    # print(type(result[0][-1]))
    # a=[('Remote Fast Query Execution  (cost=0.00..0.00 rows=0 width=0) (actual time=1957.181..1982.104 rows=597 loops=1)',), ('  Node/s: datanode_1',), ('Planning time: 0.326 ms',), ('Execution time: 1985.999 ms',)]
    # a=a[-1][0].split(' ')
    # b=float(a[2])
    # print(b)



