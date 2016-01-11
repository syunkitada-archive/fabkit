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
    CHAT: 2,
}

WARNING_STATUS_THRESHOLD = 10000


marked.setOptions {
    gfm: true,
    tables: true,
    breaks: false,
    pedantic: false,
    sanitize: true,
    smartLists: true,
    smartypants: false,
    langPrefix: 'language-',
}

hljs.initHighlightingOnLoad()
