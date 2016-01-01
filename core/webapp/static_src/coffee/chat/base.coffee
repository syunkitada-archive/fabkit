socket = io.connect(chat_connection)

socket.on 'connect', ()->
    apps.log "connected: #{chat_connection}"

chat_comment = null

socket.on 'message', (message)->
    data = JSON.parse(message)
    apps.log data

    text = data.text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    $('#chat-comments').prepend("""
      <tr>
        <td class="chat-icon">
          <span class="glyphicon glyphicon-user"></span>
        </td>
        <td>
          <span>#{data.user}</span>
          <span class="pull-right">#{data.created_at}</span>
          <br>
          #{markdown.toHTML(text)}
        </td>
      </tr>
      """)

    chat_comment.focus()

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

    for text in $('.chat-text')
        $(text).html(markdown.toHTML($(text).text()))
