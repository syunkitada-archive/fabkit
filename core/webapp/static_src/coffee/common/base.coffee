# global namespace
window.fabkit = {}

users = []
node_cluster = {}
node_clusters = []
fabscripts = []
datamap_tabs = ['status', 'relation']

graph_links = []
graph_nodes = []

mode = {
    current: 0,
    USER: 0,
    NODE: 1,
}

WARNING_STATUS_THRESHOLD = 10000
