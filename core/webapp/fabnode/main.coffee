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
user_map = {}
room_map = {}
userrooms_map = {}

http = require('http')
server = http.createServer().listen(node_port)
io = require('socket.io').listen(server)
cookie_reader = require('cookie')
querystring = require('querystring')

chatns = io.of('/chat')
chatns.use (socket, next)->
    if socket.request.headers.cookie
        cookie = cookie_reader.parse socket.request.headers.cookie
        if cookie.sessionid and cookie.csrftoken
            socket.sessionid = cookie.sessionid
            socket.csrftoken = cookie.csrftoken
            socket.is_login = false

            values = querystring.stringify({
                sessionid: socket.sessionid,
            })

            options = {
                host: hostname,
                port: port,
                path: '/user/node_get/',
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

                res.on 'data', (user)->
                    socket.is_login = true
                    socket.user = user
                    console.log "Logined #{user}"
                    user_map[socket.id] = JSON.parse(user)
                    return next()

            req.on 'error', (e)->
                console.log('problem with request: ' + e.message)
                return next(new Error('Authentication error'))

            req.write(values)
            req.end()

    else
        return next(new Error('Authentication error'))


chatns.on 'connection', (socket)->
    socket.on 'node_pipeline', (data)->
        console.log data
        # socket.send(message)

    socket.on 'join_to_room', (room)->
        if not socket.is_login
            return

        socket.join room

        socket.on 'leave_from_room', (room, fn)->
            console.log 'on leave_from_room'
            delete userrooms_map[user.user][room]
            fn('success')

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
                    chatns.to(room).emit('message', chunk)

                    for node_socket in node_sockets
                        node_socket.emit 'join_to_room', chunk, (data)->
                            console.log data

            req.on 'error', (e)->
                console.log('problem with request: ' + e.message)

            req.write(values)
            req.end()

        user = user_map[socket.id]

        socket.once 'disconnect', ->
            # socket.leave room
            room_map[room].pop(user)
            console.log 'leave room'
            console.log room_map
            socket.emit 'update_room', JSON.stringify(room_map[room])

        if room_map[room] is undefined
            room_map[room] = []

        room_map[room].push(user)
        console.log 'join room'
        console.log room_map

        if userrooms_map[user.user] is undefined
            userrooms_map[user.user] = {}
        userrooms_map[user.user][room] = {}

        socket.emit 'update_room', JSON.stringify(room_map[room])
        socket.emit 'update_userrooms', JSON.stringify(userrooms_map[user.user])

        chunk = room
        for node_socket in node_sockets
            node_socket.emit 'join_to_room', chunk, (data)->
                console.log data


chatns = io.of('/pipeline')
chatns.use (socket, next)->
    query = socket.handshake.query
    if query and query.secret == secret
        node_regexp = new RegExp(query.node)
        for node in nodes
            if node.match(node_regexp)
                return next()
    else
        return next(new Error('Authentication error'))


for node in nodes
    if node.match(my_node_regexp)
        continue

    console.log "connect to: #{node}"
    client_io = require('socket.io-client')
    node_socket = client_io.connect(node + '/pipeline', {query: "secret=#{secret}&node=#{my_node_pattern}"})
    node_socket.on 'connect', ()->
        console.log "connected"

    node_sockets.push(node_socket)
