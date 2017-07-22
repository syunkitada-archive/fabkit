users = []
node_cluster = {}
node_clusters = []
agents = []
agent_cluster = {}
agent_clusters = []
fabscripts = []
tasks = []
dns_domains = []
dns_records = []
datamap_tabs = ['status', 'relation']

graph_links = []
graph_nodes = []

chat_socket = null
chat_clusters = []
chat_cluster = 'all'

current_page = ''
current_cluster_path = ''

mode = {
    current: 0,
    USER: 0,
    NODE: 1,
    CHAT: 2,
    TASK: 3,
    EVENT: 4,
    DNS: 5,
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


time = new Date().getTime()
$(document.body).bind("mousemove keypress", (e) ->
    time = new Date().getTime()
)
