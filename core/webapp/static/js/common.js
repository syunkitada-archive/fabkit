(function() {
  var WARNING_STATUS_THRESHOLD, agent_cluster, agent_clusters, bind_shown_tab_event, change_chat_cluster, chat_cluster, chat_clusters, chat_comment, chat_socket, current_cluster, current_page, datamap_tabs, fabscripts, filter, graph_links, graph_nodes, mark_chat_text, mode, node_cluster, node_clusters, render_all, render_datamap, render_force_panel, render_node_cluster, render_node_clusters, render_partition_panel, render_table_panel, render_user, socket, update_pagedata, users,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  users = [];

  node_cluster = {};

  node_clusters = [];

  agent_cluster = {};

  agent_clusters = [];

  fabscripts = [];

  datamap_tabs = ['status', 'relation'];

  graph_links = [];

  graph_nodes = [];

  chat_socket = null;

  chat_clusters = [];

  chat_cluster = 'all';

  current_page = '';

  current_cluster = '';

  mode = {
    current: 0,
    USER: 0,
    NODE: 1,
    CHAT: 2
  };

  WARNING_STATUS_THRESHOLD = 10000;

  marked.setOptions({
    gfm: true,
    tables: true,
    breaks: false,
    pedantic: false,
    sanitize: true,
    smartLists: true,
    smartypants: false,
    langPrefix: 'language-'
  });

  hljs.initHighlightingOnLoad();

  apps.log = function(msg) {
    if (apps.debug) {
      if (typeof msg === 'string') {
        return console.log(msg);
      } else {
        return console.dir(msg);
      }
    }
  };

  filter = function() {
    var is_match, query, td, tds, tr, trs, _i, _j, _len, _len1;
    query = $(this).val();
    trs = $('tbody > tr');
    for (_i = 0, _len = trs.length; _i < _len; _i++) {
      tr = trs[_i];
      tr = $(tr);
      tds = tr.find('td');
      is_match = false;
      for (_j = 0, _len1 = tds.length; _j < _len1; _j++) {
        td = tds[_j];
        if (td.innerHTML.match(query)) {
          is_match = true;
          break;
        }
      }
      if (is_match) {
        tr.show();
      } else {
        tr.hide();
      }
    }
  };

  apps.remove_data = function(url) {
    var target_html, tr, trs, _i, _len;
    target_html = '';
    trs = $('tbody > tr');
    for (_i = 0, _len = trs.length; _i < _len; _i++) {
      tr = trs[_i];
      tr = $(tr);
      if (tr.is(':visible')) {
        if (tr.find('input[type=checkbox]').prop('checked')) {
          target_html += "<li>\n    " + (tr.find('td')[1].innerHTML) + "\n</li>\n<input type=\"hidden\" name=\"target\" value=\"" + (tr.prop('id')) + "\">";
          continue;
        }
      }
    }
    if (target_html === '') {
      target_html = '<li>Not selected</li>';
      $('#remove-submit').attr('disabled', true);
    } else {
      $('#remove-submit').attr('disabled', false);
    }
    $('#remove-form').prop('action', url);
    $('#modal-progress').hide();
    $('#modal-msg').hide();
    $('#target-list').html(target_html);
    $('#remove-modal').modal();
  };

  $('#remove-form').on('submit', function() {
    var data, form, submit_button;
    event.preventDefault(false);
    form = $(this);
    submit_button = form.find('[type=submit]');
    data = form.serialize();
    $.ajax({
      url: form.attr('action'),
      type: form.attr('method'),
      data: form.serialize(),
      beforeSend: function(xhr, settings) {
        $('#modal-progress').show();
        submit_button.attr('disabled', true);
      },
      complete: function(xhr, textStatus) {
        $('#modal-progress').hide();
      },
      success: function(data) {
        var fabscript, node, nodes, pk, target, target_list, targets, tmp_fabscripts, tmp_nodes, tmp_targets, tmp_users, user, _i, _j, _k, _l, _len, _len1, _len2, _len3, _ref, _ref1, _ref2;
        console.log(data);
        $('#modal-msg').html('<div class="bg-success msg-box">Success</div>').show();
        target_list = $('#target-list');
        targets = $('input[name=target]');
        tmp_targets = [];
        for (_i = 0, _len = targets.length; _i < _len; _i++) {
          target = targets[_i];
          tmp_targets.push(parseInt($(target).val()));
        }
        if (mode.current === mode.NODE) {
          tmp_nodes = [];
          for (_j = 0, _len1 = nodes.length; _j < _len1; _j++) {
            node = nodes[_j];
            pk = node.pk;
            if (_ref = node.pk, __indexOf.call(tmp_targets, _ref) < 0) {
              tmp_nodes.push(node);
            }
          }
          nodes = tmp_nodes;
          render_node();
        } else if (mode.current === mode.FABSCRIPT) {
          tmp_fabscripts = [];
          console.log(tmp_targets);
          console.log(fabscripts);
          for (_k = 0, _len2 = fabscripts.length; _k < _len2; _k++) {
            fabscript = fabscripts[_k];
            pk = fabscript.pk;
            if (_ref1 = fabscript.pk, __indexOf.call(tmp_targets, _ref1) < 0) {
              tmp_fabscripts.push(fabscript);
            }
          }
          fabscripts = tmp_fabscripts;
          render_fabscript();
        } else if (mode.current === mode.USER) {
          tmp_users = [];
          for (_l = 0, _len3 = users.length; _l < _len3; _l++) {
            user = users[_l];
            pk = user.pk;
            if (_ref2 = user.pk, __indexOf.call(tmp_targets, _ref2) < 0) {
              tmp_users.push(user);
            }
          }
          users = tmp_users;
          render_user();
        }
      },
      error: function(xhr, textStatus, error) {
        $('#modal-msg').html('<div class="bg-danger msg-box">Failed</div>').show();
        console.log(textStatus);
      }
    });
  });

  mark_chat_text = function() {
    var text, _i, _len, _ref, _results;
    _ref = $('.chat-text');
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      text = _ref[_i];
      _results.push($(text).html(marked($(text).text())));
    }
    return _results;
  };

  if (typeof io !== "undefined" && io !== null) {
    socket = io(chat_connection + '/chat');
    if (typeof cluster !== "undefined" && cluster !== null) {
      socket.on('connect', function() {
        apps.log("connected: " + chat_connection);
        chat_socket = socket;
        console.log(chat_socket);
        return change_chat_cluster();
      });
    }
    chat_comment = null;
    socket.on('post_comment', function(message) {
      var c, cluster, data, text, _i, _len;
      apps.log('socket.on post_comment');
      data = JSON.parse(message);
      cluster = data.cluster;
      data = JSON.parse(data.data);
      apps.log(cluster);
      apps.log(data);
      for (_i = 0, _len = chat_clusters.length; _i < _len; _i++) {
        c = chat_clusters[_i];
        if (c.cluster_name === current_cluster) {
          continue;
        }
        if (c.cluster_name === cluster) {
          c.unread_comments_length += 1;
        }
      }
      if (mode.current === mode.CHAT) {
        render_node_clusters(chat_clusters);
      }
      if (current_cluster !== cluster) {
        return;
      }
      text = data.text;
      $('#chat-comments').prepend("<tr>\n  <td class=\"chat-icon\">\n    <span class=\"glyphicon glyphicon-user\"></span>\n  </td>\n  <td>\n    <span>" + data.user + "</span>\n    <span class=\"pull-right\">" + data.created_at + "</span>\n    <br>\n    " + (marked(text)) + "\n  </td>\n</tr>");
      return chat_comment.focus();
    });
    socket.on('update_room', function(data) {
      var room;
      room = JSON.parse(data);
      return console.log(room);
    });
    chat_clusters = [];
    socket.on('update_user_clusters', function(data) {
      var user_clusters;
      apps.log('on update_user_clusters');
      apps.log(data);
      user_clusters = JSON.parse(data);
      chat_clusters = user_clusters;
      console.log("\nDEBUG");
      if (mode.current === mode.CHAT) {
        console.log(chat_clusters);
        return render_node_clusters(chat_clusters);
      }
    });
    socket.on('update_cluster_users', function(data) {
      var user, user_map, username, users_html;
      apps.log('on update_cluster_users');
      apps.log(data);
      user_map = JSON.parse(data);
      users_html = '';
      for (username in user_map) {
        user = user_map[username];
        if (user.active) {
          users_html += "<button type=\"button\" class=\"btn btn-success btn-xs\">" + user.user + "</button>";
        } else {
          users_html += "<button type=\"button\" class=\"btn btn-default btn-xs\">" + user.user + "</button>";
        }
      }
      return $('#cluster-users').html(users_html);
    });
    apps.init_chat = function() {
      apps.log('called init_chat');
      chat_comment = $('#chat-comment');
      $('#chat-comment-submit').on('click', function(event) {
        var msg;
        apps.log('on chat-comment-submit');
        msg = JSON.stringify({
          "cluster": cluster,
          "text": chat_comment.val()
        });
        if (msg) {
          socket.emit('post_comment', msg, function(data) {
            return apps.log(data);
          });
        }
        return $(chat_comment).val('');
      });
      $('#chat-leave-cluster').on('click', function(event) {
        var that;
        apps.log('on chat-leave-cluster');
        that = this;
        console.log(that);
        apps.log('clicked leave-cluster');
        socket.emit('leave_from_cluster', cluster, function(data) {
          console.log(data);
          return location.href = '/chat/';
        });
        return false;
      });
      return mark_chat_text();
    };
  } else {
    apps.init_chat = function() {
      $('#chat-room-error').html('<p class="msg-box bg-danger">Chat is not available.</p>');
      return mark_chat_text();
    };
  }

  change_chat_cluster = function() {
    if ((typeof io === "undefined" || io === null) || (chat_socket == null)) {
      return;
    }
    update_pagedata();
    apps.log("change_chat_cluster " + current_cluster);
    return chat_socket.emit('join_to_cluster', current_cluster);
  };

  render_partition_panel = function(panel_id, map) {
    var $svg, click, g, h, id, kx, ky, partition, root, svg, transform, vis, w, x, y;
    id = 'partition-svg';
    root = map.data;
    $("#" + panel_id).html("<div class=\"graph-svg-wrapper\">\n    <svg id=\"" + id + "\"></svg>\n</div>");
    id = '#partition-svg';
    svg = d3.select(id);
    $svg = $(id).empty();
    w = $svg.width();
    h = $svg.height();
    x = d3.scale.linear().range([0, w]);
    y = d3.scale.linear().range([0, h]);
    vis = d3.select(id).attr("width", w).attr("height", h);
    partition = d3.layout.partition().value(function(d) {
      return d.size;
    });
    click = function(d) {
      var kx, ky, t, _ref;
      if (!d.children) {
        return;
      }
      kx = (d.y ? w - 40 : w) / (1 - d.y);
      ky = h / d.dx;
      x.domain([d.y, 1]).range([(d.y ? 40 : 0), w]);
      y.domain([d.x, d.x + d.dx]);
      t = g.transition().duration((_ref = d3.event.altKey) != null ? _ref : {
        7500: 750
      }).attr("transform", function(d) {
        return "translate(" + x(d.y) + "," + y(d.x) + ")";
      });
      t.select("rect").attr("width", d.dy * kx).attr("height", function(d) {
        return d.dx * ky;
      });
      t.select("text").attr("transform", transform).style("opacity", function(d) {
        if (d.dx * ky > 12) {
          return 1;
        } else {
          return 0;
        }
      });
      d3.event.stopPropagation();
    };
    g = vis.selectAll("g").data(partition.nodes(root)).enter().append("svg:g").attr("transform", function(d) {
      return "translate(" + x(d.y) + "," + y(d.x) + ")";
    }).on("click", click);
    kx = w / root.dx;
    ky = h / 1;
    g.append("rect").attr("width", root.dy * kx).attr("height", function(d) {
      return d.dx * ky;
    }).attr("class", function(d) {
      if (d.children) {
        return "" + d["class"] + " parent";
      } else {
        return d["class"];
      }
    });
    transform = function(d) {
      return "translate(8," + d.dx * ky / 2 + ")";
    };
    g.append("text").attr("transform", transform).attr("dy", ".35em").style("opacity", function(d) {
      if (d.dx * ky > 12) {
        return 1;
      } else {
        return 0;
      }
    }).text(function(d) {
      if (d.type === 'status') {
        return "" + d.name + " (" + d.length + ")";
      } else {
        return "" + d.name;
      }
    });
    g.append("text").attr("transform", transform).attr("dy", ".35em").attr("y", 15).style("opacity", function(d) {
      if (d.dx * ky > 12) {
        return 1;
      } else {
        return 0;
      }
    }).text(function(d) {
      var danger_length, fabscript, success_length, warning_length, _i, _len, _ref;
      if (d.type === 'root') {
        success_length = 0;
        warning_length = 0;
        danger_length = 0;
        _ref = d.children;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          fabscript = _ref[_i];
          success_length += fabscript.success_length;
          warning_length += fabscript.warning_length;
          danger_length += fabscript.danger_length;
        }
        return "✔ " + success_length + ", ▲ " + warning_length + ", ✘ " + danger_length;
      }
      if (d.type === 'fabscript') {
        return "✔ " + d.success_length + ", ▲ " + d.warning_length + ", ✘ " + d.danger_length;
      }
    });
    return d3.select(window).on("click", function() {
      return click(root);
    });
  };

  render_force_panel = function(panel_id, map) {
    var $svg, force, h, id, link, links, node, nodes, svg, w;
    console.log(panel_id);
    console.log(map);
    id = 'force-svg';
    $("#" + panel_id).html("<div class=\"graph-svg-wrapper\">\n    <svg id=\"" + id + "\"></svg>\n</div>");
    nodes = map.data.nodes;
    links = map.data.links;
    svg = d3.select("#" + id);
    $svg = $("#" + id).empty();
    w = $svg.width();
    h = $svg.height();
    force = d3.layout.force().nodes(nodes).links(links).linkDistance(150).linkStrength(0.1).friction(0.8).charge(-300).gravity(.05).size([w, h]);
    link = svg.selectAll('.link').data(links).enter().append('line').attr('class', 'link').attr('marker-end', 'url(#markerArrow)');
    node = svg.selectAll(".node").data(nodes).enter().append('g').attr('class', 'node').call(force.drag);
    node.append('glyph').attr('class', 'glyphicon glyphicon-star').attr('unicode');
    node.append("image").attr("xlink:href", function(d) {
      return "/static/vendor/defaulticon/png/" + d.icon + ".png";
    }).attr("x", 6).attr("y", -34).attr('width', 30).attr('height', 30);
    node.append("circle").attr("r", 6).attr('class', 'node-circle');
    node.append('text').attr('dx', 12).attr('dy', '.35em').attr('class', 'node-label').text(function(d) {
      return d.name;
    });
    if (mode.current === mode.NODE) {
      node.append('text').attr('dx', 12).attr('dy', '.35em').attr('y', 16).attr('class', function(d) {
        if (d.danger_length > 0) {
          return 'node-label-danger';
        }
        if (d.warning_length > 0) {
          return 'node-label-warning';
        } else {
          return 'node-label-success';
        }
      }).text(function(d) {
        return "✔ " + d.success_length + ", ▲ " + d.warning_length + ", ✘ " + d.danger_length;
      });
    }
    force.on("tick", function(e) {
      link.attr('x1', function(d) {
        return d.source.x;
      });
      link.attr('y1', function(d) {
        return d.source.y;
      });
      link.attr('x2', function(d) {
        return d.target.x;
      });
      link.attr('y2', function(d) {
        return d.target.y;
      });
      return node.attr('transform', function(d) {
        return "translate(" + d.x + ", " + d.y + ")";
      });
    });
    return force.start();
  };

  render_datamap = function() {
    var datamap, mapname, nav_html, panel_id, tabpanels_html, _i, _len;
    datamap = node_cluster.datamap;
    for (mapname in datamap) {
      if (__indexOf.call(datamap_tabs, mapname) < 0) {
        datamap_tabs.push(mapname);
      }
    }
    nav_html = '';
    tabpanels_html = '';
    for (_i = 0, _len = datamap_tabs.length; _i < _len; _i++) {
      mapname = datamap_tabs[_i];
      panel_id = "datamap-" + mapname;
      nav_html += "<li role=\"presentation\">\n    <a id=\"map-" + mapname + "\" class=\"datamap-tab\" href=\"#" + panel_id + "\" role=\"tab\" data-toggle=\"tab\">" + mapname + "</a>\n</li>";
      tabpanels_html += "<div role=\"tabpanel\" class=\"tab-pane active\" id=\"" + panel_id + "\">\n</div>";
    }
    $('#datamap-nav').html(nav_html);
    return $('#datamap-tabpanels').html(tabpanels_html);
  };

  bind_shown_tab_event = function() {
    return $('.datamap-tab').on('shown.bs.tab', function(e) {
      var map, mapname, panel_id;
      mapname = $(e.target).html();
      panel_id = "datamap-" + mapname;
      map = node_cluster.datamap[mapname];
      if (!map.is_rendered) {
        console.log("render " + mapname);
        map.is_rendered = true;
        if (map.type === 'table') {
          render_table_panel(panel_id, map);
        } else if (map.type === 'partition') {
          render_partition_panel(panel_id, map);
        } else if (map.type === 'force') {
          render_force_panel(panel_id, map);
        }
      }
    });
  };

  render_table_panel = function(panel_id, map) {
    var index, table_html, tbody_html, td, tds, th, thead_html, ths, tr, _i, _j, _k, _l, _len, _len1, _len2, _len3, _ref, _ref1;
    thead_html = '';
    ths = [];
    tbody_html = '';
    _ref = map.data;
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      tr = _ref[_i];
      for (th in tr) {
        td = tr[th];
        if (ths.indexOf(th) === -1) {
          ths.push(th);
        }
      }
    }
    ths.sort();
    for (_j = 0, _len1 = ths.length; _j < _len1; _j++) {
      th = ths[_j];
      th = th.replace(/^![!0-9]/, '');
      thead_html += "<th>" + th + "</th>";
    }
    _ref1 = map.data;
    for (_k = 0, _len2 = _ref1.length; _k < _len2; _k++) {
      tr = _ref1[_k];
      tds = [];
      for (th in tr) {
        td = tr[th];
        index = ths.indexOf(th);
        if (index === -1) {
          index = ths.length - 1;
        }
        tds[index] = td;
      }
      tbody_html += '<tr>';
      for (_l = 0, _len3 = tds.length; _l < _len3; _l++) {
        td = tds[_l];
        tbody_html += "<td>" + td + "</td>";
      }
      tbody_html += '</tr>';
    }
    table_html = "<table id=\"datamap-table\" class=\"table table-striped table-bordered tablesorter\">\n    <thead id=\"datamap-thead\"><tr>" + thead_html + "</tr></thead>\n    <tbody id=\"datamap-tbody\">" + tbody_html + "</tbody>\n</table>";
    $("#" + panel_id).html(table_html);
    return $('#datamap-table').tablesorter({
      sortList: [[0, 0]]
    });
  };

  render_node_clusters = function(clusters) {
    var clusters_html, expand_clusters;
    update_pagedata();
    clusters_html = $("<div class=\"panel-group\" id=\"accordion\">\n</div>");
    expand_clusters = function(html, clusters, root_cluster) {
      var active, cluster, cluster_name, collapse_body, collapse_body_id, collapse_head_id, collapse_id, collapse_panel_id, name, parent_id, show, splited_cluster, tmp_clusters, tmp_name, tmp_root_cluster, _i, _len, _results;
      if (clusters == null) {
        return;
      }
      parent_id = html.prop('id');
      _results = [];
      for (_i = 0, _len = clusters.length; _i < _len; _i++) {
        cluster = clusters[_i];
        console.log(cluster);
        if (mode.current === mode.CHAT) {
          cluster_name = cluster.cluster_name;
        } else {
          cluster_name = cluster;
        }
        splited_cluster = cluster_name.split('/');
        tmp_clusters = [];
        if (splited_cluster.length > 1) {
          tmp_name = splited_cluster.slice(1).join('/');
          if (mode.current === mode.CHAT) {
            tmp_clusters.push({
              'cluster_name': tmp_name,
              'unread_comments_length': cluster.unread_comments_length
            });
          } else {
            tmp_clusters.push(tmp_name);
          }
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
            if (tmp_root_cluster === current_cluster) {
              active = 'active';
            }
            show = "<a class=\"pjax pull-right show " + active + "\" href=\"/" + current_page + "/" + tmp_root_cluster + "/\">show</a>";
            if (mode.current === mode.CHAT) {
              show = "" + show + " <span class=\"pull-right show-badge badge\">" + cluster.unread_comments_length + "</span>";
            }
          } else {
            show = "";
          }
          html.append("<div class=\"panel\" id=\"" + collapse_panel_id + "\">\n    <div class=\"panel-heading\" id=\"" + collapse_head_id + "\">\n        <span>\n            <a class=\"panel-title collapsed\" data-toggle=\"collapse\"\n                    data-parent=\"#" + parent_id + "\" href=\"#" + collapse_id + "\"\n                    aria-controls=\"" + collapse_id + "\">" + name + "</a>\n            " + show + "\n        </span>\n    </div>\n    <div id=\"" + collapse_id + "\" class=\"panel-collapse collapse\"\n            aria-labelledby=\"" + collapse_head_id + "\">\n        <div class=\"panel-body panel-group\" id=\"" + collapse_body_id + "\">\n        </div>\n    </div>\n</div>");
          collapse_body = html.find("#" + collapse_body_id);
          if (tmp_root_cluster === current_cluster && splited_cluster.length === 1) {
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
    expand_clusters(clusters_html, clusters, null);
    return $('#sidebar').html(clusters_html);
  };

  render_user = function() {
    var hash, user, users_tbody, _i, _len;
    users_tbody = $('#users-tbody');
    if (users_tbody.length > 0) {
      hash = location.hash;
      if (hash === '') {
        hash = '#user-list';
      }
      $('.user-content').hide();
      if (hash === '#user-list') {
        users_tbody.empty();
        console.log(users);
        for (_i = 0, _len = users.length; _i < _len; _i++) {
          user = users[_i];
          users_tbody.append("<tr id=\"" + user.pk + "\"> <td><input type=\"checkbox\"></td> <td>" + user.fields.username + "</td> <td>" + user.fields.is_superuser + "</td> </tr>");
        }
        $('#user-list-content').show();
      } else if (hash === '#change-password') {
        $('#change-password-content').show();
      } else if (hash === '#create-user') {
        $('#create-user-content').show();
      }
      $("#sidebar .show").removeClass('active');
      return $("#sidebar a[href=\"" + hash + "\"]").addClass('active');
    }
  };

  render_node_cluster = function() {
    var all_node_length, danger_node_length, data, fabscript, fabscript_map, fabscript_node_map, fabscript_status_map, host, i, index, is_danger, is_warning, links, name, node, node_class, node_map, nodes, nodes_tbody_html, require, result, result_html, script, status, success_node_length, sum_status, target, tmp_fabscript, warning_node_length, _i, _len, _ref, _ref1;
    console.log('Test');
    $('#markdown').html(marked($('#markdown').text()));
    fabscript_node_map = {};
    node_map = node_cluster.__status.node_map;
    fabscript_map = node_cluster.__status.fabscript_map;
    for (fabscript in fabscript_map) {
      data = fabscript_map[fabscript];
      data.children = [
        {
          type: 'status',
          name: 'success',
          "class": 'success',
          length: 0,
          children: []
        }, {
          type: 'status',
          name: 'warning',
          "class": 'warning',
          length: 0,
          children: []
        }, {
          type: 'status',
          name: 'danger',
          "class": 'danger',
          length: 0,
          children: []
        }
      ];
    }
    fabscripts = [];
    nodes_tbody_html = '';
    all_node_length = 0;
    success_node_length = 0;
    warning_node_length = 0;
    danger_node_length = 0;
    for (host in node_map) {
      node = node_map[host];
      all_node_length++;
      is_warning = false;
      is_danger = false;
      sum_status = 0;
      result_html = '<div>';
      _ref = node.fabscript_map;
      for (script in _ref) {
        result = _ref[script];
        sum_status += result.task_status + result.check_status;
        result_html += "" + script + " [" + result.task_status + "],\nsetup [" + result.status + "]: '" + result.msg + "',\ncheck [" + result.check_status + "]: '" + result.check_msg + "'\n<br>";
        node = {
          'type': node,
          'name': host,
          'size': 1
        };
        if (result.task_status > 0 || result.check_status > 0) {
          if (result.task_status < WARNING_STATUS_THRESHOLD || result.check_status < WARNING_STATUS_THRESHOLD) {
            is_warning = true;
            tmp_fabscript = fabscript_map[script].children[1];
          } else {
            is_danger = true;
            tmp_fabscript = fabscript_map[script].children[2];
          }
        } else {
          tmp_fabscript = fabscript_map[script].children[0];
        }
        tmp_fabscript.children.push(node);
        tmp_fabscript.length++;
      }
      if (is_danger) {
        node_class = 'danger';
        danger_node_length++;
      } else if (is_warning) {
        node_class = 'warning';
        warning_node_length++;
      } else {
        node_class = '';
        success_node_length++;
      }
      result_html += '</div>';
      nodes_tbody_html += "<tr class=\"" + node_class + "\">\n    <td>" + sum_status + "</td>\n    <td>" + host + "</td>\n    <td>" + result_html + "</td>\n</tr>";
    }
    $('#all-node-badge').html(all_node_length);
    $('#success-node-badge').html(success_node_length);
    $('#warning-node-badge').html(warning_node_length);
    $('#danger-node-badge').html(danger_node_length);
    $('#nodes-tbody').html(nodes_tbody_html);
    fabscript_status_map = [];
    for (fabscript in fabscript_map) {
      data = fabscript_map[fabscript];
      data.name = fabscript;
      data.type = 'fabscript';
      data.success_length = data.children[0].length;
      data.warning_length = data.children[1].length;
      data.danger_length = data.children[2].length;
      fabscript_status_map.push({
        '!!fabscript': fabscript,
        '!0success': data.success_length,
        '!1warning': data.warning_length,
        '!2danger': data.danger_length
      });
    }
    node_cluster.datamap.status = {
      'name': 'status',
      'type': 'table',
      'data': fabscript_status_map
    };
    nodes = [];
    links = [];
    index = 0;
    for (name in fabscript_map) {
      fabscript = fabscript_map[name];
      fabscript.icon = 'computer-retro';
      fabscript.index = index;
      nodes.push(fabscript);
      index++;
    }
    for (i = _i = 0, _len = nodes.length; _i < _len; i = ++_i) {
      node = nodes[i];
      _ref1 = node.require;
      for (require in _ref1) {
        status = _ref1[require];
        if (require in fabscript_map) {
          target = fabscript_map[require].index;
        } else {
          target = nodes.length;
          fabscript = {
            name: require,
            icon: 'computer-retro',
            index: target
          };
          nodes.push(fabscript);
          fabscript_map[require] = fabscript;
        }
        links.push({
          'source': i,
          'target': target
        });
      }
    }
    return node_cluster.datamap.relation = {
      'name': 'relation',
      'type': 'force',
      'data': {
        'nodes': nodes,
        'links': links
      }
    };
  };

  update_pagedata = function() {
    var paths;
    if (mode.current === mode.NODE) {
      paths = location.pathname.split('node/');
      current_page = 'node';
      current_cluster = paths[1].slice(0, -1);
      if (current_cluster === '') {
        return current_cluster = 'recent';
      }
    } else if (mode.current === mode.AGENT) {
      paths = location.pathname.split('agent/');
      current_page = 'agent';
      current_cluster = paths[1].slice(0, -1);
      if (current_cluster === '') {
        return current_cluster = 'recent';
      }
    } else if (mode.current === mode.CHAT) {
      paths = location.pathname.split('chat/');
      current_page = 'chat';
      current_cluster = paths[1].slice(0, -1);
      if (current_cluster === '') {
        return current_cluster = 'all';
      }
    }
  };

  render_all = function() {
    var tab;
    if (mode.current === mode.USER) {
      render_user();
    } else if (mode.current === mode.NODE) {
      render_node_clusters(node_clusters);
      render_node_cluster();
      $('#node-table').tablesorter({
        sortList: [[0, 1], [1, 0]]
      });
      render_datamap();
      bind_shown_tab_event();
      tab = 0;
      $('#datamap-modal').on('shown.bs.modal', function() {
        console.log('shown');
        $("#map-" + datamap_tabs[tab]).tab('show');
      });
      $('#show-datamap').on('click', function() {
        $('#datamap-modal').modal();
        tab = 0;
        if (datamap_tabs.length > 2) {
          tab = 2;
        }
      });
      $('#show-statusmap').on('click', function() {
        tab = 0;
        $('#datamap-modal').modal();
      });
      $('#show-relationmap').on('click', function() {
        tab = 1;
        $('#datamap-modal').modal();
      });
    }
    return $('[data-toggle=popover]').popover();
  };

  apps.init = function() {
    apps.log('called init');
    $('#search-input').on('change', filter).on('keyup', filter);
    $('#all-checkbox').on('change', function() {
      var is_checked, tr, trs, _i, _len;
      is_checked = $(this).prop('checked');
      trs = $('tbody > tr');
      for (_i = 0, _len = trs.length; _i < _len; _i++) {
        tr = trs[_i];
        tr = $(tr);
        if (tr.is(':visible')) {
          tr.find('input[type=checkbox]').prop('checked', is_checked);
        } else {
          tr.find('input[type=checkbox]').prop('checked', false);
        }
      }
    });
    users = $('#users');
    if (users.length > 0) {
      mode.current = mode.USER;
      users = JSON.parse(users.html());
    }
    node_clusters = $('#node_clusters');
    if (node_clusters.length > 0) {
      node_clusters = JSON.parse(node_clusters.html());
    }
    node_cluster = $('#node_cluster');
    if (node_cluster.length > 0) {
      mode.current = mode.NODE;
      node_cluster = JSON.parse(node_cluster.html());
    }
    if (location.pathname.indexOf('/agent/') === 0) {
      mode.current = mode.AGENT;
      agent_clusters = JSON.parse($('#agent_clusters').html());
      render_node_clusters(agent_clusters);
    }
    if (location.pathname.indexOf('/chat/') === 0) {
      mode.current = mode.CHAT;
    }
    render_all();
    apps.init_chat();
  };

  if ($.support.pjax) {
    $(document).pjax('.pjax', '#pjax-container');
    $(document).on('pjax:end', function() {
      var pathname;
      pathname = location.pathname.split('/', 2);
      $('.pjax').parent().removeClass('active');
      if (pathname[1] === '') {
        $('a[href="/"]').parent().addClass('active');
      } else {
        $('a[href="/' + pathname[1] + '/"]').parent().addClass('active');
      }
      apps.init();
      change_chat_cluster();
    });
  }

  $(window).on('hashchange', function() {
    if (location.hash !== '') {
      render_all();
    }
  });

}).call(this);
