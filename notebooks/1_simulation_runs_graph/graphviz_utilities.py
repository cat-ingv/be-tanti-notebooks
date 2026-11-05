import graphviz

def _define_edges(df_graph, ds_col_name='ds_name',st_col_name='step_run',rel_col_name='ds_step_relationship'):
    list_edges_graph = []
    for id_,item in df_graph.iterrows():
        ### define edges arrow
        if(item[rel_col_name]=='input' or item[rel_col_name]=='global_input' or item[rel_col_name]=='global_dataset'):
            #
            input_node = item[ds_col_name]
            output_node = item[st_col_name]
        else:
            input_node = item[st_col_name]
            output_node = item[ds_col_name]
        ### define color and style
        if(item[rel_col_name]=='global_output' or item[rel_col_name]=='global_product'):
            color = 'forestgreen'
            style = 'dashed'
        elif(item[rel_col_name]=='global_input' or item[rel_col_name]=='global_dataset'):
            color = 'forestgreen'
            style = 'dashed'
        else:
            color = 'blue'
            style = 'solid'
        ### define dictionary
        edge_dict = {'in_node': input_node,
                     'out_node': output_node,
                     'color': color,
                     'style': style}
        ### append
        list_edges_graph.append(edge_dict)
    return list_edges_graph


def _define_nodes(df_graph,ds_col_name='ds_name',sr_col_name='sr_name', rel_col_name='ds_type'):
    
    ### dataset nodes
    list_ds_nodes = [{"ds_name": item[1][ds_col_name],
                      "ds_type": item[1][rel_col_name], 
                      "is_global": (True if item[1][rel_col_name].startswith("global_") else False)} 
                         for item in df_graph[[ds_col_name,rel_col_name]].drop_duplicates().iterrows()]
    ### simulation run nodes
    list_step_nodes = df_graph[sr_col_name].unique().tolist()
    
    return list_ds_nodes,list_step_nodes


def _get_graph(name_graph,list_edges_srs_graph,list_ds_nodes=None,list_step_nodes=None,label=None):
    #
    ## define bidirect graph
    graph_srs= graphviz.Digraph(name_graph)
    #
    ## add a label
    if(label is not None):
        graph_srs.attr('graph',label=label,rankdir='LR')
    else:
        graph_srs.attr('graph',rankdir='LR')
    #
    ## add list of edges (and nodes)
    for item_edge in list_edges_srs_graph:
        graph_srs.edge(item_edge['in_node'],item_edge['out_node'],color=item_edge['color'],style=item_edge['style'])
    #
    ## personalize dataset nodes
    if(list_ds_nodes is not None):
        for ds_ in list_ds_nodes:
            if ds_["is_global"]==1:
                graph_srs.node(ds_['ds_name'],color='forestgreen',fontcolor='forestgreen',fontsize='10')
            else:
                graph_srs.node(ds_['ds_name'],color='blue',fontcolor='blue',fontsize='10')
    #
    ## personalize sr nodes
    if(list_step_nodes is not None):
        for step_ in list_step_nodes:
            graph_srs.node(step_,color='blue',shape='box',style="filled",fontcolor='white',fontsize='15')
    
    return graph_srs


def _contract_path(txt_str, num_chars=20, chars_bound=60):
    if(len(txt_str)>chars_bound):
        list_path = txt_str.split('/')
        #list_path[1] = list_path[1][:num_chars]+'...'+list_path[1][-num_chars:]
        list_path[2] = list_path[2][:num_chars]+'...'+list_path[2][-num_chars:]
        new_txt_str = '/'.join(list_path)
    else:
        new_txt_str = txt_str
    return new_txt_str
    
def build_graph_from_df(df_graph, graph_name='graph_run'):
    ### define label name for nodes
    df_graph['ds_path_label'] = df_graph['ds_path'].apply(lambda x: _contract_path(x))
    ### list edges graph
    list_edges_srs_graph = _define_edges(df_graph,ds_col_name='ds_path_label',st_col_name='sr_id',rel_col_name='ds_type')
    ### list nodes graph
    list_ds_nodes,list_step_nodes = _define_nodes(df_graph,ds_col_name='ds_path_label',sr_col_name='sr_id',rel_col_name='ds_type')
    ### create graph
    mygraph = _get_graph(graph_name,list_edges_srs_graph,list_ds_nodes,list_step_nodes)
    return mygraph

def build_graph_from_df_v2(df_graph, graph_name='graph_run'):
    ### create a label for long dataset paths
    df_graph['ds_path_label'] = df_graph['ds_path'].apply(lambda x: _contract_path(x))
    ### global input (aggregated)
    df_graph_global = df_graph[(df_graph['ds_type']=='global_input') | (df_graph['ds_type']=='global_product')]
    df_graph_global = df_graph_global.groupby(['sr_id','ds_type']).agg({
                                                                    #'ds_type': 'first',
                                                                    'ds_path_label': lambda x: "\n".join(sorted(x))})\
                                                                  .reset_index()
    ### create a common label for global_input and global_product
    df_graph_global['ds_type'] = 'global_dataset'
    list_edges_global_input = _define_edges(df_graph_global,ds_col_name='ds_path_label',st_col_name='sr_id',rel_col_name='ds_type')
    list_nodes_global_input,list_step_nodes_global_input = _define_nodes(df_graph_global,ds_col_name='ds_path_label',sr_col_name='sr_id',rel_col_name='ds_type')
    ### simulation runs datasets
    df_graph_srs = df_graph[(df_graph['ds_type']!='global_input') & (df_graph['ds_type']!='global_product')]
    list_edges_srs = _define_edges(df_graph_srs,ds_col_name='ds_path_label',st_col_name='sr_id',rel_col_name='ds_type')
    list_nodes_srs,list_step_nodes_srs = _define_nodes(df_graph_srs,ds_col_name='ds_path_label',sr_col_name='sr_id',rel_col_name='ds_type')
    ### aggregate 
    list_edges_srs_graph = list_edges_global_input + list_edges_srs
    list_ds_nodes = list_nodes_global_input + list_nodes_srs
    list_step_nodes = list(set(list_step_nodes_global_input + list_step_nodes_srs))
    ### create graph
    mygraph = _get_graph(graph_name,list_edges_srs_graph,list_ds_nodes,list_step_nodes)
    return mygraph