import numpy as np
import pyparsing as pp
import copy
PRINT_TOGGLE=False
# scale=2320515 #without cache
# scale=1
scale =412622 # with cache
test_cost=[]
table_column_name = pp.Word(pp.alphas+pp.nums+'_* "')

single_hash_cond = table_column_name + '.' + table_column_name \
  + '=' + table_column_name + '.' + table_column_name
single_hash_cond = single_hash_cond('cond*')

multi_cond = '(' + single_hash_cond +')' + pp.OneOrMore(pp.Literal('AND') + \
  pp.Literal('(') + single_hash_cond + ')')
hash_cond_parser = '(' + pp.Or([single_hash_cond, multi_cond]) + ')'

def simple_repr(plan):
  node_type = plan['Node Type']
  mapping = dict([
    ('Hash Join', 'Hash Cond'),
    ('Merge Join', 'Merge Cond'),
    ('Nested Loop', 'Join Filter')
  ])
  return '[{}]/[{}]({}..{}): {}'.format(node_type, plan.get('Join Type'), \
    plan.get('Startup Cost'), plan.get('Total Cost'), plan.get(mapping.get(node_type)))
class estimator():
  def __init__(self,db,greedy=False) -> None:
    if greedy:
      self.env_cache=db
    else:
      self.env_cache=copy.deepcopy(db)
      # self.env_cache=db
      # self.greedy=greedy
  def _estimate_network_cost(self,plan, num_nodes, alias_dict):
    if 'Plans' in plan:
      children_costs = list()
      for subnode in plan['Plans']:
        cost=self._estimate_network_cost(subnode, num_nodes, alias_dict)
        children_costs.append(cost)

      # children_costs.append(_estimate_network_cost(subnode, env, num_nodes, alias_dict))
      current_cost = self.estimate_network_cost_for_single_plan_node(plan, num_nodes, alias_dict) 
      # current_cost = estimate_network_cost_for_single_plan_node(plan, env, num_nodes, alias_dict) 
      return (sum(children_costs) + current_cost)
    else:
      # cost = # rows * width
      return 0

  def estimate_network_cost_for_single_plan_node(self,plan,num_nodes, alias_dict):
    name = plan['Node Type']
    if 'Join' in name:
      if PRINT_TOGGLE:
        print('computing cost for ', simple_repr(plan))
      sub_costs = list()
      for subplan in plan['Plans']:
        if subplan['Parent Relationship'] not in ['Outer', 'Inner']:
          continue
        sub_cost = subplan['Plan Rows'] * subplan['Plan Width']
        sub_costs.append(sub_cost)
      # let's estimate
      # parse details.
      # find hash cond 
      cost = None
      if name == 'Hash Join': # hash left/right/semi join
        cost = self.estimate_hash_join_cost(plan, sub_costs,num_nodes, alias_dict)
      elif name.startswith('Merge'): # merge left/right/full join
        print('Merge')
      #   cost = estimate_merge_join_cost(plan, sub_costs, partition_scheme, num_nodes)
      elif name.startswith('Nested Loop'): # nested loop anti/left/semi join
        print('Nested Loop')
        # cost = estimate_nested_loop_join_cost(plan, sub_costs, partition_scheme, num_nodes)
      else:
        assert False, 'Join type [{}] is not handled'.format(name)
      if PRINT_TOGGLE:
        print('cost:', cost)
      return cost
    elif 'Nested Loop' in name:
      if PRINT_TOGGLE:
        print('computing cost for ', simple_repr(plan))
      # TODO: FIXME: we currently perform a repatitioned join; could be optimized.
      sub_costs = list()
      for subplan in plan['Plans']:
        cost = subplan['Plan Rows'] * subplan['Plan Width']
        sub_costs.append(cost)
      cost = sum(sub_costs)
      if PRINT_TOGGLE:
        print('cost:', cost)
      return cost
    # elif 'Append' in name:
    #   # TODO: FIXME: we may need to consider the result as a temporal table and distribute it.
    #   # append node, assume no network cost
    #   return 0
    else:
      if PRINT_TOGGLE:
        print('ignore node ', simple_repr(plan))
      sub_plans = plan['Plans']
      sub_plans = list(filter(lambda x: x['Parent Relationship'] == 'Outer', sub_plans))
      # assert only one node. ()
      assert len(sub_plans) <= 1, \
        'expecting only one child, but got {}; \n{}'.format(len(sub_plans), plan)
      return 0
  def estimate_hash_join_cost(self,plan, sub_costs, num_nodes, alias_dict=None):
    # print('parsing', cond_str, sub_costs)
    cond_str = plan['Hash Cond']
    matched_arr = hash_cond_parser.parseString(cond_str)
    conditions = matched_arr.asDict()['cond']
    # multiple conditions
    table_column_list_dict = {}
    left_table, right_table = None, None
    for cond in conditions:
      left_table, left_column = cond[0].strip(), cond[2].strip()
      right_table, right_column = cond[4].strip(), cond[6].strip()
      if left_table not in table_column_list_dict:
        table_column_list_dict[left_table]=[]
      if right_table not in table_column_list_dict:
        table_column_list_dict[right_table]=[]
      table_column_list_dict[left_table].append(left_column)
      table_column_list_dict[right_table].append(right_column)
      # print(left_table,right_table)
    # exit()
    assert len(table_column_list_dict) == 2, \
      'Too many tables! expecting 2 but got [{}:{}]'.format(len(table_column_list_dict), table_column_list_dict.keys())
    assert len(table_column_list_dict[left_table]) == len(conditions), 'assertion failed'
    assert len(table_column_list_dict[right_table]) == len(conditions), 'assertion failed'
    left_join_columns = set(table_column_list_dict[left_table])
    right_join_columns = set(table_column_list_dict[right_table])

    is_left_partitioned=True
    is_right_partitioned=True
    # TODO some attrs are partitioned keys, while others are not? In general, hash join has only two participants
    for attr in left_join_columns:
      if self.env_cache.partition_scheme[left_table][attr]==0:
        is_left_partitioned=False
        break
    for attr in right_join_columns:
      if self.env_cache.partition_scheme[right_table][attr]==0:
        is_right_partitioned=False
        break
    # print(left_join_columns,left_table)

    is_left_replicated = self.env_cache.replicated_table[left_table]
    is_right_replicated = self.env_cache.replicated_table[right_table]
    # print(left_table, left_join_columns, right_table, right_join_columns)
    # print('left, right', is_left_partitioned, is_right_partitioned)
    left_cost, right_cost = sub_costs
    # print(left_cost,right_cost)

    ## SEPARATE ESTIMATION
    if (is_left_partitioned and is_right_partitioned) or \
    (is_left_replicated and is_right_partitioned) or\
        (is_left_partitioned and is_right_replicated):
      # okay!
      if PRINT_TOGGLE:
        print('co-partitioned', is_left_partitioned, is_right_partitioned)
          # is_left_replicated, is_right_replicated)
      return 0
    else:
      left_colocated_cost=0 if is_left_partitioned else left_cost
      right_colocated_cost=0 if is_right_partitioned else right_cost
      left_broadcast_join = 0 if is_left_replicated else left_cost*num_nodes
      right_broadcast_join = 0 if is_right_replicated else right_cost*num_nodes
      repartitioned_join_cost=left_colocated_cost+right_colocated_cost     
      broadcast_join = min(left_broadcast_join, right_broadcast_join)
      if PRINT_TOGGLE:
        print('repartition', repartitioned_join_cost, 'broadcast', broadcast_join)
      if broadcast_join < repartitioned_join_cost:
        # add broadcast 
        if left_cost < right_cost:
          # add left
          if not is_left_replicated and left_table!='lineorder':
            self.env_cache.replicated_table[left_table]=1
        else:
          # add right
          if not is_right_replicated and right_table!='lineorder':
            # partition_scheme.add_scheme(right_table, replicate=True)
            self.env_cache.replicated_table[right_table]=1
            # print('right broadcasted')
        if PRINT_TOGGLE:
          print('select broadcast join')
      else:
        # repartition join, add both schemes
        if not is_left_partitioned:
          # self.env_cache.partition((left_table,left_join_columns))
          for col in left_join_columns:
            self.env_cache.partition_scheme[left_table][col]=1
          # partition_scheme.add_scheme(left_table, column_set=set(left_join_columns))
        if not is_right_partitioned:
          for col in right_join_columns:
            self.env_cache.partition_scheme[right_table][col]=1
          # partition_scheme.add_scheme(right_table, column_set=set(right_join_columns))
        if PRINT_TOGGLE:
          print('select repartition join')

      return min(repartitioned_join_cost, broadcast_join)
import json,os
def cost_estimate(env,greedy):
  costs=[]
  root='demo/'
  e=estimator(env,greedy)
  files=['q1-1.json','q1-2.json','q1-3.json',\
         'q2-1.json','q2-2.json','q2-3.json',\
         'q3-1.json','q3-2.json','q3-3.json',\
         'q4-1.json','q4-2.json','q4-3.json']
  for file in files:
    with open(os.path.join(root,file)) as fp:
      plan=json.load(fp)
      # costs.append(e._estimate_network_cost(plan[0][0][0]['Plan'],2,0))
      cost=e._estimate_network_cost(plan[0][0][0]['Plan'],2,0)
      costs.append(cost)
      # print(file)
      # print(cost)
      # print(_estimate_network_cost(plan[0][0][0]['Plan'],db.partition_scheme,0,0)) 
      fp.close()
  return -np.array([sum(costs)])/scale

# from env import env
# if __name__ == "__main__":
#   db=env()
#   # db.partition_scheme['lineorder']['lo_orderkey']=1
#   # db.partition_scheme['lineorder']['lo_linenumber']=1
#   # db.partition_scheme['supplier']['s_suppkey']=1
#   # db.partition_scheme['part']['p_partkey']=1
#   # db.partition_scheme['customer']['c_custkey']=1
#   # db.partition_scheme['dim_date']['d_datekey']=1 
#   print(cost_estimate(db))
