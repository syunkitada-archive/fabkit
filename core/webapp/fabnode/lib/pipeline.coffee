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
            socket.on 'post_comment', (data)->
                logger.all.info "pipeline: post_comment: #{data}"
                chat.io.emit('post_comment', data)

            socket.on 'join_user', (data)->
                logger.all.info "pipeline: join_user: #{data}"
                data = JSON.parse(data)
                cluster = data.cluster
                user = data.data

                for cluster in user.user_clusters
                    cluster_name = cluster.cluster_name
                    if context.cluster_users_map[cluster_name] is undefined
                        context.cluster_users_map[cluster_name] = {}

                    if context.cluster_users_map[cluster_name][user.user] is undefined
                        user.active = 0
                        context.cluster_users_map[cluster_name][user.user] = user

                    context.cluster_users_map[cluster_name][user.user].active = 1
                    cluster_users = JSON.stringify(context.cluster_users_map[cluster_name])
                    chat.io.to(cluster_name).emit('update_cluster_users', cluster_users)


            socket.on 'leave_from_cluster', (data)->
                data = JSON.parse(data)
                cluster = data.cluster
                user = data.data

                if context.cluster_users_map[cluster][user.user]?
                    delete context.cluster_users_map[cluster][user.user]

                console.log "\n\nDEBUG"
                console.log context.cluster_users_map

                cluster_users = JSON.stringify(context.cluster_users_map[cluster])
                chat.io.to(cluster).emit('update_cluster_users', cluster_users)

            socket.on 'leave_user', (data)->
                logger.all.debug "pipeline: leave_user: #{data}"
                data = JSON.parse(data)
                cluster = data.cluster
                user = data.data

                console.log "\n\nleave_user DEBUG"
                console.log context.cluster_users_map
                console.log user
                console.log user.user_clusters
                for cluster in user.user_clusters
                    cluster_name = cluster.cluster_name
                    console.log cluster_name
                    console.log context.cluster_users_map[cluster_name]
                    if context.cluster_users_map[cluster_name][user.user]?
                        context.cluster_users_map[cluster_name][user.user].active = 0
                    cluster_users = JSON.stringify(context.cluster_users_map[cluster_name])
                    chat.io.to(cluster_name).emit('update_cluster_users', cluster_users)

        for node in config.nodes
            logger.all.info "connect to: #{node}"
            client_io = require('socket.io-client')
            node_socket = client_io.connect(node + '/pipeline', {query: "secret_key=#{config.secret_key}&node=#{config.my_node_pattern}"})
            node_socket.on 'connect', ()->
                logger.all.info "conneced"

            context.node_sockets.push(node_socket)
}
