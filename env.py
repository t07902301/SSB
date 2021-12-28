import yaml
error=False
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
        self.replicated_table={}
        self.db_config={}
        n_attr=0
        for table,attributes in dumped['tables'].items():
            # db_config[table]={"action":1}
            self.replicated_table[table]=0
            self.partition_scheme[table]={}
            for attr in attributes:
                self.partition_scheme[table][attr]=0   
            self.db_config[table]=[(n_attr,n_attr+len(attributes)),attributes]
            n_attr+=len(attributes)
        with open('foreign_key.txt','r') as fw:
            key_pairs=fw.readlines()

        self.fk_edges={} #((tbl_1,attr_1),(tbl_2,attr_2))=is_activated
        for pair in key_pairs:
            pair=pair.strip('\n').replace(' ','').split('=')
            edge=[]
            for each in pair:
                for table,attributes in dumped['tables'].items():
                    if each in attributes:
                        edge.append((table,each))
            self.fk_edges[(edge[0],edge[1])]=0   

        self.fk_info={} #tbl_1=[((tbl_1,attr_1),(tbl_2,attr_2))]
        self.get_fk_info()
        # self.action_type=['partition','replicate','activate',"deactivate"]
    def get_fk_info(self):
        for pair in self.fk_edges:
            if pair[0][0] not in self.fk_info:
                self.fk_info[pair[0][0]]=[]
            if pair[1][0] not in self.fk_info:
                self.fk_info[pair[1][0]]=[]            
            self.fk_info[pair[0][0]].append(pair)
            self.fk_info[pair[1][0]].append(pair)
    def replicate(self,table):
      if self.replicated_table[table]==0:
        self.replicated_table[table]=1
        for attr in self.partition_scheme[table]:
            self.partition_scheme[table][attr]=0
        for edge in self.fk_info[table]:
            self.deactivate(edge)   
      # else:
      #   self.replicated_table[table]=0 #TODO Better undo?
      # print(self.replicated_table)
    def reset(self):
        for tbl in self.partition_scheme:
            tbl_attr=self.partition_scheme[tbl]
            for attr in tbl_attr:
                tbl_attr[attr]=0
            self.partition_scheme[tbl]=tbl_attr
        for edge in self.fk_edges:
            self.fk_edges[edge]=0
        for tbl in self.replicated_table:
            self.replicated_table[tbl]=0
    def partition(self,pair):
        table,attr=pair
        if self.partition_scheme[table][attr]==0:
          for edge in self.fk_info[table]:
              if pair not in edge and self.fk_edges[edge]==1:
                  self.deactivate(edge)
          for each in self.db_config[table][1]: #Only one attr can be partitioned key
              self.partition_scheme[table][each]=0                    
          self.partition_scheme[table][attr]=1
          self.replicated_table[table]=0
        # else:
        #   self.replicate(table)

        # display(self.partition_scheme)
    def step(self,action_idx):
        n_fk_edges=4
        n_tables_attr=58
        # old_state=self.get_current_state()
        if action_idx<n_fk_edges:
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
                self.replicated_table[tbl_1]=0
                self.replicated_table[tbl_2]=0
                msg='activate {}'.format(edge)
            else:
                # self.fk_edges[edge]=0
                # tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be Deactivated
                # self.partition_scheme[tbl_1][tbl_1_attr]=0
                # self.partition_scheme[tbl_2][tbl_2_attr]=0  
                self.deactivate(edge)   
                msg='deactivate {}'.format(edge)
        elif action_idx<n_fk_edges+n_tables_attr:
            action_idx-=n_fk_edges
            for table,attr_info in self.db_config.items():
                attr_range=attr_info[0]
                if action_idx>= attr_range[0] and action_idx<attr_range[1]:
                    break
            attr_list=attr_info[1]
            attr=attr_list[action_idx-attr_range[0]]  
            pair=(table,attr)
            self.partition(pair)
            msg='partition {}'.format(attr)
        else:
            action_idx-=n_fk_edges+n_tables_attr
            table_list=list(self.partition_scheme.keys())
            table=table_list[action_idx]
            if table=='lineoder':
              error=True
            self.replicate(table)
            for edge in self.fk_info[table]:
                self.deactivate(edge)
            msg='replicate {}'.format(table)
        return  self.get_current_state(),msg 
    def get_current_state(self):
        return np.array([list(self.fk_edges.values())+ self.get_table_states()])
    def deactivate(self,edge):
        self.fk_edges[edge]=0
        tbl_1,tbl_1_attr,tbl_2,tbl_2_attr=edge[0][0],edge[0][1],edge[1][0],edge[1][1] # to be Deactivated
        if tbl_1=='lineorder':
            self.partition_scheme[tbl_1][tbl_1_attr]=0
            self.replicate(tbl_2)
        elif tbl_2=='lineorder':
            self.partition_scheme[tbl_2][tbl_2_attr]=0
            self.replicate(tbl_1)
        else:
            self.replicate(tbl_1)
            self.replicate(tbl_2)
    def cost_estimate(self):
        # TODO partition scheme and plans
        pass
    def get_table_states(self):
        # self.table_states=[]
        table_states=[]
        for table,attributes in self.partition_scheme.items():
            table_states+=[self.replicated_table[table]]+list(attributes.values()) 
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



