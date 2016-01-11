module.exports = {
    init: ()->
        lib = global.lib
        context = lib.context
        config = lib.config
        logger = lib.logger
        webapi = lib.webapi
        chat = lib.chat

        this.io = context.io.of('/pipeline')
        this.io.use (socket, next)->
            logger.all.debug "pipeline: called pipelinens.use"
            socket.is_login = false

            query = socket.handshake.query
            if query and query.secret_key == config.secret_key
                node_regexp = new RegExp(query.node)
                for node in config.nodes
                    if node.match(config.node_regexp)
                        socket.is_login = true
                        logger.all.debug "pipeline: login success"
                        return next()
            else
                logger.error "pipeline: Authentication error"
                return next(new Error('Authentication error'))

        this.io.on 'connection', (socket)->
            socket.on 'message', (data)->
                data = JSON.parse(data)
                chat.io.to(data.room).emit('message', data.data)

            socket.on 'join_to_room', (data)->
                data = JSON.parse(data)
                room = data.room
                user = data.data
                if context.user_rooms_map[user.user] is undefined
                    context.user_rooms_map[user.user] = {}
                context.user_rooms_map[user.user][room] = {}

                if context.room_users_map[room] is undefined
                    context.room_users_map[room] = {}

                if context.room_users_map[room][user.user] is undefined
                    user.active = 0
                    context.room_users_map[room][user.user] = user

                context.room_users_map[room][user.user].active += 1

                room_users = JSON.stringify(context.room_users_map[room])
                chat.io.to(room).emit('update_room_users', room_users)

            socket.on 'leave_from_room', (data)->
                data = JSON.parse(data)
                room = data.room
                user = data.data
                delete context.user_rooms_map[user.user][room]

                delete context.room_users_map[room][user.user]
                room_users = JSON.stringify(context.room_users_map[room])
                chat.io.to(room).emit('update_room_users', room_users)

            socket.on 'disconnect_socket', (data)->
                logger.all.debug "pipeline: disconnect: #{data}"
                data = JSON.parse(data)
                room = data.room
                user = data.data

                context.room_users_map[room][user.user].active -= 1
                room_users = JSON.stringify(context.room_users_map[room])
                chat.io.to(room).emit('update_room_users', room_users)


        for node in config.nodes
            logger.all.info "connect to: #{node}"
            client_io = require('socket.io-client')
            node_socket = client_io.connect(node + '/pipeline', {query: "secret_key=#{config.secret_key}&node=#{config.my_node_pattern}"})
            node_socket.on 'connect', ()->
                logger.all.info "conneced"

            context.node_sockets.push(node_socket)
}
