import json,os
partition_types=['1','2']
path='plans/{}'.format(partition_types[0])
compared_path='plans/{}'.format(partition_types[1])

for root, dirs, files in os.walk(path):
    for name in files:
        # print(os.path.join(root, name))
        # print(name)
        with open(os.path.join(path,name), 'r') as f:
            plan_content=json.load(f)
        with open(os.path.join(compared_path,name), 'r') as f:
            compared_plan_content=json.load(f)   
        if compared_plan_content==plan_content:
            print('yes')         
            print(name)