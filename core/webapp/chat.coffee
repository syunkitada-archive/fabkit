http = require('http')
server = http.createServer().listen(4000)
io = require('socket.io').listen(server)
cookie_reader = require('cookie')
querystring = require('querystring')

redis = require('redis')
sub = redis.createClient()

# Subscribe to the Redis chat channel
sub.subscribe('chat')


io.use (socket, next)->
    cookie = cookie_reader.parse socket.request.headers.cookie
    if cookie.sessionid and cookie.csrftoken
        socket.sessionid = cookie.sessionid
        socket.csrftoken = cookie.csrftoken
        return next()

    return next(new Error('Authentication error'))


io.sockets.on 'connection', (socket)->

    # Grab message from Redis and send to client
    sub.on 'message', (channel, message)->
        socket.send(message)

    # Client is sending message through socket.io
    socket.on 'send_message', (message)->
        console.log(message)
        values = querystring.stringify({
            data: message,
            sessionid: socket.sessionid,
        })

        options = {
            host: '192.168.11.50',
            port: 8000,
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
                console.log('BODY: ' + chunk)

        req.on 'error', (e)->
            console.log('problem with request: ' + e.message)

        req.write(values)
        req.end()
