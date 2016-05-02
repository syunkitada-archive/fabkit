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

                    webapi.request(socket, '/user/node/login/', {},
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
            socket.on 'join_to_cluster', (cluster)->
                if not socket.is_login
                    return

                user = context.user_map[socket.id]

                if not context.user_map[socket.id].joined_cluster?
                    socket.join cluster
                    context.user_map[socket.id].joined_cluster = cluster

                    user_clusters = JSON.stringify(user['user_clusters'])
                    socket.emit('update_user_clusters', user_clusters)
                    that.publish_pipeline(cluster, 'join_user', user)

                else
                    if cluster != context.user_map[socket.id].joined_cluster
                        socket.leave context.user_map[socket.id].joined_cluster
                        socket.join cluster
                        context.user_map[socket.id].joined_cluster = cluster

                    webapi.request(socket, '/user/node/login/', {},
                        (data)->
                            logger.all.info "chat: update user: #{data}"
                            context.user_map[socket.id] = JSON.parse(data)
                            user = context.user_map[socket.id]
                            user_clusters = JSON.stringify(user['user_clusters'])
                            socket.emit('update_user_clusters', user_clusters)

                            cluster_users = JSON.stringify(context.cluster_users_map[cluster])
                            socket.emit('update_cluster_users', cluster_users)
                        ,
                        (e)->
                            logger.error.error "chat: Authentication error: #{e.message}"
                    )

                logger.all.info "chat: #{user.user} join to #{cluster}"
                context.dump()

            socket.on 'leave_from_cluster', (cluster, fn)->
                if not context.user_map[socket.id]?
                    fn()

                user = context.user_map[socket.id]
                logger.all.debug "chat: on leave_from_cluster"

                webapi.request(socket, '/chat/node/leave_from_cluster/', {
                    'cluster': cluster,
                },
                    (data)->
                        user_clusters = []
                        for user_cluster in user['user_clusters']
                            if user_cluster.cluster_name == cluster
                                continue

                            user_clusters.push(user_cluster)

                        context.user_map[socket.id]['user_clusters'] = user_clusters

                        that.publish_pipeline(cluster, 'leave_from_cluster', user)
                        logger.all.info "chat: leave_from_cluster: #{data}"
                        fn()
                    ,
                    (e)->
                        logger.error.error "chat: leave_from_cluster error: #{e.message}"
                        fn()
                )

            socket.on 'post_comment', (message, fn)->
                if not context.user_map[socket.id]?
                    fn()

                user = context.user_map[socket.id]
                logger.all.debug "chat: socket.on post_comment: #{message}"
                that.post_comment(socket, message)
                fn()

            socket.once 'disconnect', ->
                if not context.user_map[socket.id]?
                    return

                user = context.user_map[socket.id]
                logger.all.debug "chat: socket: disconnect"
                that.publish_pipeline(user.joined_cluster, 'leave_user', user)
                if context.user_map[socket.id]?
                    delete context.user_map[socket.id]

        logger.all.debug 'chat: initialized'

    post_comment: (socket, message)->
        that = this
        msg = JSON.parse(message)
        cluster = msg['cluster']
        user = context.user_map[socket.id]
        logger.all.info "chat: on post_comment: user=#{user.user}, message=#{message}"

        webapi.request socket, '/chat/node/post_comment/', {
                message: message,
            }
            , (data)->
                that.publish_pipeline(cluster, 'post_comment', data)

                logger.all.info "chat: emit to #{cluster}: #{data}"

                data = JSON.parse(data)
                text = data.text
                if text.indexOf('!fab ') == 0
                    text = text.replace('!fab ', 'fab ')
                    logger.all.debug "chat: exec: #{text}"

                    exec text, (err, stdout, stderr)->
                        if err
                            logger.error.error "chat: exec: stderr: #{stderr}"
                            result_text = stderr
                        else
                            logger.all.debug "chat: exec: stdout #{stdout}"
                            result_text = stdout

                        if result_text.length > 10000
                            result_text = result_text.slice(0, 2000) + "\n...\n\n" + result_text.slice(-8000)

                        data['text'] = "``` bash\n$ #{text}\n#{result_text}```"
                        data = JSON.stringify(data)
                        console.log data
                        # that.post_comment(socket, data)
                        that.publish_pipeline(cluster, 'post_comment', data)

            , (e)->
                logger.error.error "problem with request: #{e.message}"


    publish_pipeline: (cluster, event_name, data)->
        logger.all.debug "chat: publish_pipeline: cluster=#{cluster}, event_name=#{event_name}"
        req_data = {
            'cluster': cluster,
            'data': data,
        }
        req_data = JSON.stringify(req_data)

        for node_socket in context.node_sockets
            logger.all.debug "publish"
            node_socket.emit event_name, req_data
}
