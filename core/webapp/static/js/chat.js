(function() {
  var chat_comment, socket;

  socket = io.connect(chat_connection);

  socket.on('connect', function() {
    return apps.log("connected: " + chat_connection);
  });

  chat_comment = null;

  socket.on('message', function(message) {
    var data, text;
    data = JSON.parse(message);
    apps.log(data);
    text = data.text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    $('#chat-comments').prepend("<tr>\n  <td class=\"chat-icon\">\n    <span class=\"glyphicon glyphicon-user\"></span>\n  </td>\n  <td>\n    <span>" + data.user + "</span>\n    <span class=\"pull-right\">" + data.created_at + "</span>\n    <br>\n    " + (markdown.toHTML(text)) + "\n  </td>\n</tr>");
    return chat_comment.focus();
  });

  apps.init_chat = function() {
    var text, _i, _len, _ref, _results;
    apps.log('called init_chat');
    chat_comment = $('#chat-comment');
    $('#chat-comment-submit').on('click', function(event) {
      var msg;
      msg = JSON.stringify({
        "cluster": cluster,
        "text": chat_comment.val()
      });
      if (msg) {
        socket.emit('send_message', msg, function(data) {
          return apps.log(data);
        });
      }
      return $(chat_comment).val('');
    });
    _ref = $('.chat-text');
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      text = _ref[_i];
      _results.push($(text).html(markdown.toHTML($(text).text())));
    }
    return _results;
  };

}).call(this);
