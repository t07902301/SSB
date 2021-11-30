# from numpy.lib.function_base import append
import yaml
import numpy as np
# from estimator import *
# import json,os
class env():
    def __init__(self) -> None:

        with open("db_config.yaml", "r") as stream:
            try:
                dumped=yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.partition_scheme={}
        self.db_config={}
        n_attr=0
        for table,attributes in dumped['tables'].items():
            # db_config[table]={"action":1}
            self.partition_scheme[table]={}
            for attr in attributes:
                self.partition_scheme[table][attr]=0   
            self.db_config[table]=[(n_attr,n_attr+len(attributes)),attributes]
            n_attr+=len(attributes)   

        # with open('db_config.json', 'r') as fp:
        #     db_config = json.load(fp)        
        with open('foreign_key.txt','r') as fw:
            key_pairs=fw.readlines()

        fk_edges={}
        for pair in key_pairs:
            pair=pair.strip('\n').replace(' ','').split('=')
            edge=[]
            for each in pair:
                for table,attributes in dumped['tables'].items():
                    if each in attributes:
                        edge.append((table,each))
            fk_edges[(edge[0],edge[1])]=0   

        self.fk_edges=fk_edges  

        self.fk_edges_init=fk_edges.copy()
        self.init_ps=self.partition_scheme.copy()

        # self.table_states=table_states
        # self.query_states=[1]*12
        # self.db_config={
        #     "customer": [(0,8)],
        #     "dim_date":(8,25),
        #     "lineorder":(25,42),
        #     "part": (42,51),
        #     "supplier": (51,58)
        # }
        self.fk_info={}
        self.get_fk_info()
        # self.action_type=['partition','replicate','activate',"deactivate"]
    def get_fk_info(self):
        for table_pair,is_activated in self.fk_edges.items():
            if table_pair[0][0] not in self.fk_info:
                self.fk_info[table_pair[0][0]]=[]
            if table_pair[1][0] not in self.fk_info:
                self.fk_info[table_pair[1][0]]=[]            
            self.fk_info[table_pair[0][0]].append(table_pair)
            self.fk_info[table_pair[1][0]].append(table_pair)
    def decode_table_states(self,states,in_action=True):
        if in_action:
            tables=states[:5]
            attrs=states[5:63]
        else:
            attrs=states
        pass
    def is_partitioned(self,table,attrs):
        pass
    def reset(self):
        self.partition_scheme=self.init_ps.copy()
        self.fk_edges=self.fk_edges_init.copy()
    def step(self,action_idx):
        fk_edges_number=4
        # tables_attr_number=58
        # old_state=self.get_current_state()
        if action_idx<fk_edges_number:
            candidates=list(self.fk_edges.keys())
            edge=candidates[action_idx]
            if self.fk_edges[edge]==0:
                tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be activated
                for e in self.fk_info[tbl_1]:
                    if (tbl_1,tbl_1_attr) not in e and self.fk_edges[e]==1:
                        self.deactivate(e)
                        break
                for e in self.fk_info[tbl_2]:
                    if (tbl_2,tbl_2_attr) not in e and self.fk_edges[e]==1:
                        self.deactivate(e)
                        break            
                self.fk_edges[edge]=1
                self.partition_scheme[tbl_1][tbl_1_attr]=1
                self.partition_scheme[tbl_2][tbl_2_attr]=1
            else:
                # self.fk_edges[edge]=0
                # tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be Deactivated
                # self.partition_scheme[tbl_1][tbl_1_attr]=0
                # self.partition_scheme[tbl_2][tbl_2_attr]=0  
                self.deactivate(edge)                
        else:
            for table,attr_info in self.db_config.items():
                attr_range=attr_info[0]
                if action_idx> attr_range[0] and action_idx<attr_range[1]:
                    break
            attr_list=attr_info[1]
            self.partition_scheme[table][attr_list[action_idx-attr_range[0]]]=1 if self.partition_scheme[table][attr_list[action_idx-attr_range[0]]]==0 else 0

            ## Old method of partitioning tables
            # tables_list=list(self.table_range.keys())
            # table_idx=np.where(tables==1)
            # attr_idx=np.where(attrs==1)
            # # self.partition_scheme[]
            # for idx in table_idx:
            #     table_changed=tables_list[idx]
            #     attr_range=self.table_range[table_changed]
            #     attr_list=list(self.partition_scheme[table_changed].keys())
            #     for i in attr_idx:
            #         if i<attr_range[0] or i>attr_range[1]:
            #             break
            #         self.partition_scheme[table_changed][attr_list[i]]=1              
        return  self.get_current_state()  
    def get_current_state(self):
        return np.array(list(self.fk_edges.values())+ self.get_table_states())
        # action_type=action[:4] #only one at a time
        # tables=action[4:9] # TODO a single table when partitioning?
        # attrs=action[5:63]
        # fk_edges=action[67:]
        # action_idx=np.where(action_type==1)
        # if action_idx==0:
        #     tables_list=list(self.table_range.keys())
        #     table_idx=np.where(tables==1)
        #     attr_idx=np.where(attrs==1)
        #     # self.partition_scheme[]
        #     for idx in table_idx:
        #         table_changed=tables_list[idx]
        #         attr_range=self.table_range[table_changed]
        #         attr_list=list(self.partition_scheme[table_changed].keys())
        #         for i in attr_idx:
        #             if i<attr_range[0] or i>attr_range[1]:
        #                 break
        #             self.partition_scheme[table_changed][attr_list[i]]=1
        # elif action_idx==1:
        #     tables_list=list(self.table_range.keys())
        #     table_idx=np.where(tables==1)
        #     attr_idx=np.where(attrs==1)
        #     # self.partition_scheme[]
        #     for idx in table_idx:
        #         table_changed=tables_list[idx]
        #         attr_range=self.table_range[table_changed]
        #         attr_list=list(self.partition_scheme[table_changed].keys())
        #         for i in attr_idx:
        #             if i<attr_range[0] or i>attr_range[1]:
        #                 break
        #             self.partition_scheme[table_changed][attr_list[i]]=0
        #         # TODO table states changed? actions?
                
        # elif action_idx==2:
        #     #TODO only one edge affected at a time? 
        #     candidate_idx=np.where(fk_edges)
        #     candidates=list(self.fk_edges.keys())
        #     for idx in candidate_idx:
        #         edge=candidates[idx]
        #         tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be activated
        #         for e in self.fk_info[tbl_1]:
        #             if (tbl_1,tbl_1_attr) not in e and self.fk_edges[e]==1:
        #                 self.deactivate(e)
        #                 break
        #         for e in self.fk_info[tbl_2]:
        #             if (tbl_2,tbl_2_attr) not in e and self.fk_edges[e]==1:
        #                 self.deactivate(e)
        #                 break            
        #         self.fk_edges[edge]=1
        #         self.partition_scheme[tbl_1][tbl_1_attr]=1
        #         self.partition_scheme[tbl_2][tbl_2_attr]=1
        #         self.edge_operation(edge,1)
        # else:
        #     #TODO only edge affected at a time?
        #     candidate_idx=np.where(fk_edges)
        #     candidates=list(self.fk_edges.keys())
        #     for idx in candidate_idx:
        #         edge=candidates[idx]   
        #         assert self.fk_edges[edge]==1, "Edge {} not activated yet".format(edge)    
        #         # self.edge_operation(edge,0)
        #         self.fk_edges[edge]=0
        #         tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be Deactivated
        #         self.partition_scheme[tbl_1][tbl_1_attr]=0
        #         self.partition_scheme[tbl_2][tbl_2_attr]=0   
    def deactivate(self,edge):
        self.fk_edges[edge]=0
        tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be Deactivated
        self.partition_scheme[tbl_1][tbl_1_attr]=0
        self.partition_scheme[tbl_2][tbl_2_attr]=0
    def cost_estimate(self):
        # TODO partition scheme and plans
        pass
    def get_table_states(self):
        # self.table_states=[]
        table_states=[]
        for table,attributes in self.partition_scheme.items():
            table_states+=list(attributes.values()) 
            # print(table,list(attributes.values()),len(list(attributes.values())))

        # print(len(self.table_states))
        return table_states
def main():
# if __name__ == "__main__":
    db=env()
    # print(len(db.table_states))
    # print(type(db.partition_scheme))
    # print(db.query_states)
    print(db.fk_edges)
    db.get_table_states()
# import yaml
# db_config={}
# with open("db_config.yaml", "r") as stream:
#     try:
#         dumped=yaml.safe_load(stream)
#         # print(type())
#         # print(dumped.keys())
#         # print(dumped['tables']["customer"])
#     except yaml.YAMLError as exc:
#         print(exc)
# # for table,attributes in dumped['tables'].items():
#     # db_config[table]={"action":0}
#     # for attr in attributes:
#     #     db_config[table][attr]=0

# # # print(db_config["customer"])
# # table_states=[]
# # for table,attributes in db_config.items():
# #     table_states+=list(attributes.values())
# # # print(len(table_states))

# with open('foreign_key.txt','r') as fw:
#     key_pairs=fw.readlines()

# fk_edges=[]
# for pair in key_pairs:
#     pair=pair.strip('\n').replace(' ','').split('=')
#     edge=[]
#     for each in pair:
#         for table,attributes in dumped['tables'].items():
#             if each in attributes:
#                 edge.append((table,each))
#     fk_edges.append(edge)
# print(fk_edges)

# import json

# # with open('db_config.json', 'w') as fp:
# #     json.dump(db_config, fp,indent=4)

# import os
# sqlCommands=[]
# for root, dirs, files in os.walk('queries'):
#     for file in files:
#         fd = open(os.path.join(root,file), 'r')
#         sqlFile = fd.read()
#         fd.close()
#         sqlCommands.append(sqlFile)
# for idx in (len(sqlCommands)-1):
#     if sqlCommands[idx]==sqlCommands[idx+1]:
#         print(True,idx,idx+1)



