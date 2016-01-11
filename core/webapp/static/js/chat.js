(function() {
  var chat_comment, render_userrooms, socket;

  socket = io(chat_connection + '/chat');

  socket.on('connect', function() {
    apps.log("connected: " + chat_connection);
    return socket.emit('join_to_room', cluster, function(data) {
      apps.log("joined " + cluster);
      return apps.log(data);
    });
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

  socket.on('update_room', function(data) {
    var room;
    room = JSON.parse(data);
    return console.log(room);
  });

  socket.on('update_userrooms', function(data) {
    var room, roomdata, rooms, userrooms;
    if (mode.current === mode.CHAT) {
      console.log(data);
      userrooms = JSON.parse(data);
      rooms = [];
      for (room in userrooms) {
        roomdata = userrooms[room];
        if (room === 'all') {
          continue;
        }
        rooms.push(room);
      }
      rooms.sort();
      rooms.splice(0, 0, 'all');
      return render_userrooms(rooms);
    }
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

  render_userrooms = function(userrooms) {
    var cluster_path, clusters_html, expand_clusters, page, paths;
    paths = location.pathname.split('chat/');
    page = 'chat';
    cluster_path = paths[1].slice(0, -1);
    if (cluster_path === '') {
      cluster_path = 'all';
    }
    clusters_html = $("<div class=\"panel-group\" id=\"accordion\">\n</div>");
    expand_clusters = function(html, clusters, root_cluster) {
      var active, cluster_name, collapse_body, collapse_body_id, collapse_head_id, collapse_id, collapse_panel_id, name, parent_id, show, splited_cluster, tmp_clusters, tmp_name, tmp_root_cluster, _i, _len, _results;
      parent_id = html.prop('id');
      _results = [];
      for (_i = 0, _len = clusters.length; _i < _len; _i++) {
        cluster_name = clusters[_i];
        splited_cluster = cluster_name.split('/');
        tmp_clusters = [];
        if (splited_cluster.length > 1) {
          tmp_name = splited_cluster.slice(1).join('/');
          tmp_clusters.push(tmp_name);
        }
        name = splited_cluster[0];
        if (root_cluster === null) {
          tmp_root_cluster = name;
        } else {
          tmp_root_cluster = root_cluster + '/' + name;
        }
        collapse_id = "" + parent_id + "-" + name;
        collapse_panel_id = "" + parent_id + "-panel-" + name;
        collapse_head_id = "" + parent_id + "-head-" + name;
        collapse_body_id = "" + parent_id + "-body-" + name;
        collapse_body = html.find("#" + collapse_body_id);
        if (collapse_body.length === 0) {
          active = '';
          if (splited_cluster.length === 1) {
            tmp_root_cluster = tmp_root_cluster.replace(/__/g, '/');
            if (tmp_root_cluster === cluster_path) {
              active = 'active';
            }
            show = "<a class=\"pjax pull-right show " + active + "\" href=\"/" + page + "/" + tmp_root_cluster + "/\">show</a>";
          } else {
            show = "";
          }
          html.append("<div class=\"panel\" id=\"" + collapse_panel_id + "\">\n    <div class=\"panel-heading\" id=\"" + collapse_head_id + "\">\n        <span>\n            <a class=\"panel-title collapsed\" data-toggle=\"collapse\"\n                    data-parent=\"#" + parent_id + "\" href=\"#" + collapse_id + "\"\n                    aria-controls=\"" + collapse_id + "\">" + name + "</a>\n            " + show + "\n        </span>\n    </div>\n    <div id=\"" + collapse_id + "\" class=\"panel-collapse collapse\"\n            aria-labelledby=\"" + collapse_head_id + "\">\n        <div class=\"panel-body panel-group\" id=\"" + collapse_body_id + "\">\n        </div>\n    </div>\n</div>");
          collapse_body = html.find("#" + collapse_body_id);
          if (tmp_root_cluster === cluster_path && splited_cluster.length === 1) {
            html.find("#" + collapse_id).parents('.collapse').addClass('in');
            html.find("#" + collapse_panel_id).parents('.panel').find('> .panel-heading .panel-title').removeClass('collapsed');
          }
        }
        if (tmp_clusters.length > 0) {
          _results.push(expand_clusters(collapse_body, tmp_clusters, tmp_root_cluster));
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };
    expand_clusters(clusters_html, userrooms, null);
    return $('#sidebar').html(clusters_html);
  };

}).call(this);
