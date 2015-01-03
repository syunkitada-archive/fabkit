# global namespace
window.fabkit = {}

users = []
nodes = []
fabscripts = []
results = []

graph_links = []
graph_nodes = []

mode = {
    current: 0,
    HOME: 0,
    USER: 1,
    NODE: 2,
    FABSCRIPT: 3,
    RESULT: 4,
}

WARNING_STATUS_THRESHOLD = 10000
