fs = require('fs')
ini = require('ini')

config_ini = ini.parse(fs.readFileSync('../../../../fabfile.ini', 'utf-8'))

debug = config_ini.web.debug
debug = true if debug is undefined

hostname = config_ini.web.hostname
hostname = 'localhost' if hostname is undefined

port = config_ini.web.port
port = 8080 if port is undefined

secret_key = config_ini.DEFAULT.secret_key
secret_key = 'changeme' if secret_key is undefined

node_port = config_ini.web.node_port
node_port = 4000 if node_port is undefined

nodes = config_ini.web.nodes
nodes = ["http://#{hostname}:#{node_port}"] if nodes is undefined

my_node_pattern = ".*://#{hostname}:#{node_port}$"
my_node_regexp = new RegExp(my_node_pattern)

module.exports = {
    debug: debug,
    hostname: hostname,
    port: port,
    secret_key: secret_key,
    nodes: nodes,
    node_port: node_port,
    my_node_pattern: my_node_pattern,
    my_node_regexp: my_node_regexp,
}
