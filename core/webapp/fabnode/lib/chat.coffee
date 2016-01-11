cookie_reader = require('cookie')
querystring = require('querystring')
exec = require('child_process').exec


lib = null
context = null
config = null
logger = null
webapi = null
pipeline = null

module.exports = {
    init: ()->
        that = this
        lib = global.lib
        context = lib.context
        config = lib.config
        logger = lib.logger
        webapi = lib.webapi
        pipeline = lib.pipeline

        this.io = context.io.of('/chat')
        this.io.use (socket, next)->
            logger.all.debug "chat: called io.use"

            if socket.request.headers.cookie
                cookie = cookie_reader.parse socket.request.headers.cookie
                if cookie.sessionid and cookie.csrftoken
                    socket.sessionid = cookie.sessionid
                    socket.csrftoken = cookie.csrftoken
                    socket.is_login = false

                    webapi.request(socket, '/user/node_get/', {},
                        (data)->
                            socket.is_login = true
                            socket.user = data
                            logger.all.info "chat: login success: #{data}"
                            context.user_map[socket.id] = JSON.parse(data)
                            return next()
                        ,
                        (e)->
                            logger.error.error "chat: Authentication error: #{e.message}"
                            return next(new Error('Authentication error'))
                    )

            else
                logger.error.error "chat: Authentication error: cookie not found"
                return next(new Error('Authentication error'))


        this.io.on 'connection', (socket)->
            socket.on 'join_to_room', (room)->
                if not socket.is_login
                    return

                user = context.user_map[socket.id]

                socket.on 'leave_from_room', (room, fn)->
                    logger.all.debug "chat: on leave_from_room"
                    delete context.user_rooms_map[user.user][room]
                    that.publish_pipeline(room, 'leave_from_room', user)
                    fn()

                socket.on 'send_message', (message)->
                    logger.all.info "chat: on send_message: user=#{user.user}, message=#{message}"

                    webapi.request socket, '/chat/node_api', {
                            data: message,
                        }
                        , (data)->
                            that.publish_pipeline(room, 'message', data)

                            logger.all.info "chat: emit to #{room}: #{data}"

                            data = JSON.parse(data)
                            text = data.text
                            if text.indexOf('!') == 0
                                text = text.slice(1)
                                logger.all.debug "chat: exec: #{text}"
                                if text.indexOf('fab ') == 0
                                    exec text, (err, stdout, stderr)->
                                        if err
                                            logger.error.error "chat: exec: stderr: #{stderr}"
                                            text = stderr
                                        else
                                            logger.all.debug "chat: exec: stdout #{stdout}"
                                            text = stdout

                                        data = {
                                            "text": "``` bash\n#{text}\n```",
                                            "user": "fabric",
                                            "created_at": "2016-01-11 09:27:06.253494+00:00",
                                            "updated_at": "2016-01-11 09:27:06.253494+00:00",
                                        }
                                        data = JSON.stringify(data)
                                        that.publish_pipeline(room, 'message', data)

                                else
                                    exec 'fab -l', (err, stdout, stderr)->
                                        logger.all.debug "chat: exec #{stdout}"

                        , (e)->
                            logger.error.error "problem with request: #{e.message}"

                socket.once 'disconnect', ->
                    logger.all.debug "chat: socket: disconnect"
                    that.publish_pipeline(room, 'disconnect_socket', user)

                socket.join room

                if context.user_rooms_map[user.user] is undefined
                    context.user_rooms_map[user.user] = {}
                context.user_rooms_map[user.user][room] = {}

                user_rooms = JSON.stringify(context.user_rooms_map[user.user])
                socket.emit('update_user_rooms', user_rooms)
                that.publish_pipeline(room, 'join_to_room', user)

                logger.all.info "chat: #{user.user} join to #{room}"
                context.dump()

        logger.all.debug 'chat: initialized'

    publish_pipeline: (room, event_name, data)->
        logger.all.debug "chat: publish_pipeline: room=#{room}, event_name=#{event_name}"
        req_data = {
            'room': room,
            'data': data,
        }
        req_data = JSON.stringify(req_data)

        for node_socket in context.node_sockets
            node_socket.emit event_name, req_data
}
