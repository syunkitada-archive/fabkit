mark_chat_text = ->
    for text in $('.chat-text')
        $(text).html(marked($(text).text()))

if io?
    socket = io(chat_connection + '/chat')

    if current_cluster?
        socket.on 'connect', ()->
            apps.log "connected: #{chat_connection}"
            chat_socket = socket
            console.log chat_socket
            change_chat_cluster()

    chat_comment = null

    socket.on 'post_comment', (message)->
        apps.log 'socket.on post_comment'
        data = JSON.parse(message)
        cluster = data.cluster
        data = JSON.parse(data.data)
        apps.log cluster
        apps.log data

        for c in chat_clusters
            if c.cluster_name == current_cluster
                continue
            if c.cluster_name == cluster
                c.unread_comments_length += 1

        if mode.current == mode.CHAT
            render_node_clusters(chat_clusters)

        if current_cluster != cluster
            return

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

    chat_clusters = []
    socket.on 'update_user_clusters', (data)->
        apps.log 'on update_user_clusters'
        apps.log data
        user_clusters = JSON.parse(data)
        # for room, roomdata of userrooms
        #     if room == 'all'
        #         continue
        #     room_clusters.push room

        # room_clusters.sort()
        # room_clusters.splice(0, 0, 'all')
        chat_clusters = user_clusters
        console.log "\nDEBUG"

        if mode.current == mode.CHAT
            console.log chat_clusters
            render_node_clusters(chat_clusters)

    socket.on 'update_cluster_users', (data)->
        apps.log 'on update_cluster_users'
        apps.log data
        user_map = JSON.parse(data)
        users_html = ''
        for username, user of user_map
            if user.active
                users_html += """<button type="button" class="btn btn-success btn-xs">#{user.user}</button>"""

            else
                users_html += """<button type="button" class="btn btn-default btn-xs">#{user.user}</button>"""

        $('#cluster-users').html(users_html)

    apps.init_chat = ()->
        apps.log('called init_chat')
        chat_comment = $('#chat-comment')

        $('#chat-comment-submit').on 'click', (event)->
            apps.log('on chat-comment-submit')
            msg = JSON.stringify({
                "cluster": current_cluster,
                "text": chat_comment.val(),
            })

            if (msg)
                socket.emit 'post_comment', msg, (data)->
                    apps.log(data)

            $(chat_comment).val('')

        $('#chat-leave-cluster').on 'click', (event)->
            apps.log('on chat-leave-cluster')
            that = this
            console.log that
            apps.log 'clicked leave-cluster'
            socket.emit 'leave_from_cluster', cluster, (data)->
                console.log data
                location.href = '/chat/'

            return false

        mark_chat_text()

else
    apps.init_chat = ()->
        $('#chat-room-error').html('<p class="msg-box bg-danger">Chat is not available.</p>')

        mark_chat_text()

change_chat_cluster = () ->
    if not io? or not chat_socket?
        return

    update_pagedata()

    apps.log "change_chat_cluster #{current_cluster}"
    chat_socket.emit 'join_to_cluster', current_cluster
