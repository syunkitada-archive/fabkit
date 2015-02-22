# global namespace
window.fabkit = {}

users = []
node_cluster = {}
node_clusters = []
fabscripts = []

graph_links = []
graph_nodes = []

mode = {
    current: 0,
    HOME: 0,
    USER: 1,
    NODE: 2,
    FABSCRIPT: 3,
}

WARNING_STATUS_THRESHOLD = 10000
