mark_chat_text = ->
    for text in $('.chat-text')
        $(text).html(marked($(text).text()))

if io?
    socket = io(chat_connection + '/chat')

    socket.on 'connect', ()->
        apps.log "connected: #{chat_connection}"
        socket.emit 'join_to_room', cluster, (data)->
            apps.log "joined #{cluster}"
            apps.log data

    chat_comment = null

    socket.on 'message', (message)->
        data = JSON.parse(message)
        apps.log data

        # text = data.text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
        text = data.text
        $('#chat-comments').prepend("""
          <tr>
            <td class="chat-icon">
              <span class="glyphicon glyphicon-user"></span>
            </td>
            <td>
              <span>#{data.user}</span>
              <span class="pull-right">#{data.created_at}</span>
              <br>
              #{marked(text)}
            </td>
          </tr>
          """)

        chat_comment.focus()

    socket.on 'update_room', (data)->
        room = JSON.parse(data)
        console.log room

    room_clusters = []
    socket.on 'update_user_rooms', (data)->
        apps.log 'on update_user_rooms'
        apps.log data
        userrooms = JSON.parse(data)
        for room, roomdata of userrooms
            if room == 'all'
                continue
            room_clusters.push room

        room_clusters.sort()
        room_clusters.splice(0, 0, 'all')

        if mode.current == mode.CHAT
            render_node_clusters(room_clusters)

    socket.on 'update_room_users', (data)->
        apps.log 'on update_room_users'
        apps.log data

    apps.init_chat = ()->
        apps.log('called init_chat')
        chat_comment = $('#chat-comment')

        $('#chat-comment-submit').on 'click', (event)->
            msg = JSON.stringify({
                "cluster": cluster,
                "text": chat_comment.val(),
            })

            if (msg)
                socket.emit 'send_message', msg, (data)->
                    apps.log(data)

            $(chat_comment).val('')

        $('#chat-leave-room').on 'click', (event)->
            that = this
            console.log that
            apps.log 'clicked leave-room'
            socket.emit 'leave_from_room', cluster, (data)->
                console.log data
                location.href = that.href

            return false

        mark_chat_text()

else
    apps.init_chat = ()->
        $('#chat-room-error').html('<p class="msg-box bg-danger">Chat is not available.</p>')

        mark_chat_text()
