fs = require('fs')
ini = require('ini')

output = ini.parse(fs.readFileSync('../../../../fabfile.ini', 'utf-8'))

hostname = output.web.hostname
hostname = 'localhost' if hostname is undefined
port = output.web.port
port = 8080 if port is undefined
secret = output.DEFAULT.secret
secret = 'changeme' if secret is undefined
node_port = output.web.node_port
node_port = 4000 if node_port is undefined
nodes = output.web.nodes
nodes = [] if nodes is undefined
node_sockets = []
nodes = [
    'http://192.168.11.50:4000',
    'http://192.168.11.50:4001',
]
my_node_pattern = ".*://#{hostname}:#{node_port}$"
my_node_regexp = new RegExp(my_node_pattern)

http = require('http')
server = http.createServer().listen(node_port)
io = require('socket.io').listen(server)
cookie_reader = require('cookie')
querystring = require('querystring')

io.use (socket, next)->
    query = socket.handshake.query
    console.log query
    if query and query.secret == secret
        node_regexp = new RegExp(query.node)
        for node in nodes
            if node.match(node_regexp)
                return next()

    if socket.request.headers.cookie
        cookie = cookie_reader.parse socket.request.headers.cookie
        if cookie.sessionid and cookie.csrftoken
            socket.sessionid = cookie.sessionid
            socket.csrftoken = cookie.csrftoken
            return next()

    return next(new Error('Authentication error'))


io.sockets.on 'connection', (socket)->
    socket.on 'node_message', (message)->
        console.log message
        socket.send(message)

    # Client is sending message through socket.io
    socket.on 'send_message', (message)->
        console.log(message)
        values = querystring.stringify({
            data: message,
            sessionid: socket.sessionid,
        })

        options = {
            host: hostname,
            port: port,
            path: '/chat/node_api',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': values.length
            }
        }

        req = http.request options, (res)->
            console.log('STATUS: ' + res.statusCode)
            console.log('HEADERS: ' + JSON.stringify(res.headers))
            res.setEncoding('utf8')

            res.on 'data', (chunk)->
                socket.send(chunk)
                for node_socket in node_sockets
                    node_socket.emit 'node_message', chunk, (data)->
                        console.log data

        req.on 'error', (e)->
            console.log('problem with request: ' + e.message)

        req.write(values)
        req.end()


for node in nodes
    if node.match(my_node_regexp)
        continue

    console.log "connect to: #{node}"
    client_io = require('socket.io-client')
    node_socket = client_io.connect(node, {query: "secret=#{secret}&node=#{my_node_pattern}"})
    node_socket.on 'connect', ()->
        console.log "connected"

    node_sockets.push(node_socket)
