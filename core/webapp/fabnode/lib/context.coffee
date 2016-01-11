http = require('http')


config = null
logger = null

module.exports = {
    init: ()->
        lib = global.lib
        config = lib.config
        logger = lib.logger

        server = http.createServer().listen(config.node_port)
        this.io = require('socket.io').listen(server)

        logger.all.debug 'context: initialized'

    dump: ()->
        if config.debug
            logger.all.debug "context: node_sockets: #{this.node_sockets}"
            logger.all.debug "context: user_map: #{JSON.stringify(this.user_map, null, '  ')}"
            logger.all.debug "context: room_users_map: #{JSON.stringify(this.room_users_map, null, '  ')}"
            logger.all.debug "context: userrooms_map: #{JSON.stringify(this.user_rooms_map, null, '  ')}"

    node_sockets: []  # changeto pipeline

    # {user} = {user: 'hoge', active: 0}
    user_map: {}  # {socket1.id: {user}, socket2.id: {user2}, ... }
    user_rooms_map: {}  # {user1: {room1: {userroom}, room2: {userroom}}, user2: ... }
    room_users_map: {}  # {room1: {user1: {usea}
}
