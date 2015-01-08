(function() {
  var WARNING_STATUS_THRESHOLD, fabscripts, filter, graph_links, graph_nodes, init, mode, node_clusters, nodes, render_all, render_fabscript, render_force_layout, render_node, render_node_clusters, render_result, render_user, results, users,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.fabkit = {};

  users = [];

  nodes = [];

  node_clusters = [];

  fabscripts = [];

  results = [];

  graph_links = [];

  graph_nodes = [];

  mode = {
    current: 0,
    HOME: 0,
    USER: 1,
    NODE: 2,
    FABSCRIPT: 3,
    RESULT: 4
  };

  WARNING_STATUS_THRESHOLD = 10000;

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

  fabkit.remove_data = function(url) {
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
        var fabscript, node, pk, result, target, target_list, targets, tmp_fabscripts, tmp_nodes, tmp_results, tmp_targets, tmp_users, user, _i, _j, _k, _l, _len, _len1, _len2, _len3, _len4, _m, _ref, _ref1, _ref2, _ref3;
        console.log(data);
        $('#modal-msg').html('<div class="bg-success msg-box">Success</div>').show();
        target_list = $('#target-list');
        targets = $('input[name=target]');
        tmp_targets = [];
        for (_i = 0, _len = targets.length; _i < _len; _i++) {
          target = targets[_i];
          tmp_targets.push(parseInt($(target).val()));
        }
        if ($('#nodes-tbody').length > 0) {
          tmp_nodes = [];
          for (_j = 0, _len1 = nodes.length; _j < _len1; _j++) {
            node = nodes[_j];
            pk = node.pk;
            if (_ref = node.pk, __indexOf.call(tmp_targets, _ref) < 0) {
              tmp_nodes.push(node);
            }
          }
          nodes = tmp_nodes;
        } else if ($('#fabscripts-tbody').length > 0) {
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
          console.log(fabscripts);
        } else if ($('#results-tbody').length > 0) {
          tmp_results = [];
          for (_l = 0, _len3 = results.length; _l < _len3; _l++) {
            result = results[_l];
            pk = result.pk;
            if (_ref2 = result.pk, __indexOf.call(tmp_targets, _ref2) < 0) {
              tmp_results.push(result);
            }
          }
          results = tmp_results;
        } else if ($('#users-tbody').length > 0) {
          tmp_users = [];
          for (_m = 0, _len4 = users.length; _m < _len4; _m++) {
            user = users[_m];
            pk = user.pk;
            if (_ref3 = user.pk, __indexOf.call(tmp_targets, _ref3) < 0) {
              tmp_users.push(user);
            }
          }
          users = tmp_users;
        }
        console.log('DEBUG');
        render_all();
      },
      error: function(xhr, textStatus, error) {
        $('#modal-msg').html('<div class="bg-danger msg-box">Failed</div>').show();
        console.log(textStatus);
      }
    });
  });

  render_force_layout = function() {
    var $svg, force, h, id, link, links, node, svg, w;
    id = '#graph-svg';
    nodes = graph_nodes;
    links = graph_links;
    svg = d3.select(id);
    $svg = $(id).empty();
    w = $svg.width();
    h = $svg.height();
    force = d3.layout.force().nodes(nodes).links(links).linkDistance(150).linkStrength(0.1).friction(0.8).charge(-300).gravity(.04).size([w, h]);
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
    if (mode.current === mode.RESULT) {
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

  render_node_clusters = function() {
    var active, cluster_pk, clusters_html, node_cluster, page, paths, _i, _len;
    console.log('test');
    console.log(node_clusters);
    paths = location.pathname.split('/', 3);
    page = paths[1];
    cluster_pk = parseInt(paths[2]);
    if (cluster_pk === 0) {
      active = 'active';
    } else {
      active = '';
    }
    clusters_html = "<li class=\"" + active + "\"><a class=\"pjax\" href=\"/" + page + "/0/\">root</a></li>";
    for (_i = 0, _len = node_clusters.length; _i < _len; _i++) {
      node_cluster = node_clusters[_i];
      active = '';
      if (node_cluster.pk === cluster_pk) {
        active = "active";
      }
      clusters_html += "<li class=\"" + active + "\"> <a class=\"pjax\" href=\"/" + page + "/" + node_cluster.pk + "/\"> " + node_cluster.fields.name + "</a> </li>";
    }
    return $('#node-clusters-ul').html(clusters_html);
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
        $('#user-list').show();
      } else if (hash === '#change-password') {
        $('#change-password').show();
      } else if (hash === '#create-user') {
        $('#create-user').show();
      }
      $("#left-nav > li").removeClass('active');
      return $("" + hash + "-li").addClass('active');
    }
  };

  render_fabscript = function() {
    var active, cluster, cluster_data, fabscript, fabscript_cluster_map, fabscript_clusters_ul, fabscripts_tbody, hash, i, is_exist, linked, linked_html, linked_index, node, node_index, scripts, _i, _j, _k, _l, _len, _len1, _len2, _len3, _len4, _m, _ref, _ref1;
    hash = location.hash;
    if (hash === '') {
      hash = '#all';
    }
    if (hash === '#all') {
      $('#show-graph').hide();
    } else {
      $('#show-graph').show();
    }
    graph_nodes = [];
    graph_links = [];
    fabscript_cluster_map = {
      'all': fabscripts
    };
    fabscripts_tbody = '';
    for (_i = 0, _len = fabscripts.length; _i < _len; _i++) {
      fabscript = fabscripts[_i];
      linked_html = '';
      _ref = fabscript.fields.linked_fabscripts;
      for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
        linked = _ref[_j];
        linked_html += "" + linked + "</br>";
      }
      cluster = fabscript.fields.name.split('.')[0];
      if (cluster in fabscript_cluster_map) {
        cluster_data = fabscript_cluster_map[cluster];
        cluster_data.push(fabscript);
      } else {
        cluster_data = [fabscript];
      }
      fabscript_cluster_map[cluster] = cluster_data;
      if (hash === '#all' || hash === ("#" + cluster)) {
        fabscripts_tbody += "<tr id=\"" + fabscript.pk + "\"> <td><input type=\"checkbox\"></td> <td>" + fabscript.fields.name + "</td> <td>" + linked_html + "</td> <td>" + fabscript.fields.updated_at + "</td> </tr>";
        if (hash !== "#all") {
          is_exist = false;
          node_index = 0;
          for (i = _k = 0, _len2 = graph_nodes.length; _k < _len2; i = ++_k) {
            node = graph_nodes[i];
            if (node.name === fabscript.fields.name) {
              is_exist = true;
              node_index = i;
              break;
            }
          }
          if (!is_exist) {
            node_index = graph_nodes.length;
            graph_nodes.push({
              'name': fabscript.fields.name
            });
          }
          _ref1 = fabscript.fields.linked_fabscripts;
          for (_l = 0, _len3 = _ref1.length; _l < _len3; _l++) {
            linked = _ref1[_l];
            linked = linked.split(':')[0];
            is_exist = false;
            linked_index = 0;
            for (i = _m = 0, _len4 = graph_nodes.length; _m < _len4; i = ++_m) {
              node = graph_nodes[i];
              if (node.name === linked) {
                is_exist = true;
                linked_index = i;
                break;
              }
            }
            if (!is_exist) {
              linked_index = graph_nodes.length;
              graph_nodes.push({
                'name': linked
              });
            }
            if (node_index !== linked_index) {
              graph_links.push({
                'source': linked_index,
                'target': node_index
              });
            }
          }
        }
      }
    }
    $('#fabscripts-tbody').html(fabscripts_tbody);
    fabscript_clusters_ul = '';
    for (cluster in fabscript_cluster_map) {
      scripts = fabscript_cluster_map[cluster];
      active = "";
      if (hash === ("#" + cluster)) {
        active = "active";
      }
      fabscript_clusters_ul += "<li class=\"" + active + "\">\n    <a href=\"#" + cluster + "\">\n    " + cluster + " (" + scripts.length + ")\n    </a>\n</li>";
    }
    return $('#fabscript-clusters-ul').html(fabscript_clusters_ul);
  };

  render_node = function() {
    var data, data_html, host_html, key, node, nodes_tbody_html, value, _i, _len;
    nodes_tbody_html = '';
    for (_i = 0, _len = nodes.length; _i < _len; _i++) {
      node = nodes[_i];
      data = JSON.parse(node.fields.data);
      console.log(data);
      if (Object.keys(data).length === 0) {
        data_html = "No data";
      } else {
        data_html = "<table class='table table-bordered'><tbody>";
        for (key in data) {
          value = data[key];
          data_html += "<tr>\n    <td>" + key + "</td>\n    <td>" + value + "</td>\n</tr>";
        }
        data_html += '</tbody></table>';
      }
      host_html = "<a class=\"popover-anchor\" data-containe=\"body\" data-toggle=\"popover\"\n    data-placement=\"bottom\" data-html=\"true\" data-title=\"Data\" data-content=\"" + data_html + "\">\n    " + node.fields.host + "\n</a>";
      nodes_tbody_html += "<tr id=\"" + node.pk + "\"> <td><input type=\"checkbox\"></td> <td>" + node.fields.path + "</td> <td>" + host_html + "</td> <td>" + node.fields.ip + "</td> <td>" + node.fields.uptime + "</td> <td>" + node.fields.ssh + "</td> </tr>";
    }
    $('#nodes-tbody').empty().html(nodes_tbody_html);
    return render_node_clusters();
  };

  render_result = function() {
    var danger_length, fabscript, fabscript_node, fabscript_node_map, i, index, link, linked_fabscript, log, logs_all, logs_all_html, logs_html, name, node, result, results_tbody_html, script_name, success_length, timestamp, tmp_logs_html, tr_class, warning_length, _i, _j, _k, _l, _len, _len1, _len2, _len3, _m, _ref, _ref1, _results;
    render_node_clusters();
    fabscript_node_map = {};
    results_tbody_html = '';
    for (i = _i = 0, _len = results.length; _i < _len; i = ++_i) {
      result = results[i];
      tmp_logs_html = '';
      _ref = JSON.parse(result.fields.logs);
      for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
        log = _ref[_j];
        node = {
          'index': i,
          'name': result.fields.node_path
        };
        if (!(log.fabscript in fabscript_node_map)) {
          fabscript_node_map[log.fabscript] = {
            'links': [],
            'success_nodes': [],
            'warning_nodes': [],
            'danger_nodes': []
          };
        }
        if (log.status === 0) {
          fabscript_node_map[log.fabscript]['success_nodes'].push(node);
        } else if (log.status < WARNING_STATUS_THRESHOLD) {
          fabscript_node_map[log.fabscript]['warning_nodes'].push(node);
        } else {
          fabscript_node_map[log.fabscript]['danger_nodes'].push(node);
        }
        tmp_logs_html += "" + log.fabscript + ": " + log.msg + "[" + log.status + "]<br>";
      }
      logs_all_html = '';
      logs_all = JSON.parse(result.fields.logs_all);
      if (logs_all.length === 0) {
        logs_all_html = 'No data';
      } else {
        for (_k = logs_all.length - 1; _k >= 0; _k += -1) {
          log = logs_all[_k];
          timestamp = new Date(log.timestamp * 1000);
          logs_all_html += "" + log.fabscript + ": " + log.msg + "[" + log.status + "] " + timestamp + "<br>";
        }
      }
      logs_html = "<a class=\"popover-anchor\" data-containe=\"body\" data-toggle=\"popover\"\n    data-placement=\"bottom\" data-html=\"true\" data-title=\"Logs all\" data-content=\"" + logs_all_html + "\">\n    " + tmp_logs_html + "\n</a>";
      if (result.fields.status === 0) {
        tr_class = '';
      } else if (result.fields.status < WARNING_STATUS_THRESHOLD) {
        tr_class = 'warning';
      } else {
        tr_class = 'danger';
      }
      results_tbody_html += "<tr id=\"" + result.pk + "\" class=\"" + tr_class + "\"> <td><input type=\"checkbox\"></td> <td>" + result.fields.node_path + "</td> <td>" + result.fields.status + "</td> <td>" + result.fields.msg + "</td> <td>" + logs_html + "</td> <td>" + result.fields.updated_at + "</td> </tr>";
    }
    $('#results-tbody').html(results_tbody_html);
    index = 0;
    for (_l = 0, _len2 = fabscripts.length; _l < _len2; _l++) {
      fabscript = fabscripts[_l];
      name = fabscript.fields.name;
      if (!(name in fabscript_node_map)) {
        continue;
      }
      fabscript_node_map[name].index = index;
      if ('icon' in fabscript.fields.data) {
        fabscript_node_map[name].icon = fabscript.fields.data.icon;
      } else {
        fabscript_node_map[name].icon = 'computer-retro';
      }
      _ref1 = fabscript.fields.linked_fabscripts;
      for (_m = 0, _len3 = _ref1.length; _m < _len3; _m++) {
        linked_fabscript = _ref1[_m];
        script_name = linked_fabscript.split(':')[0];
        if (!(script_name in fabscript_node_map)) {
          fabscript_node_map[script_name] = {
            'links': [],
            'success_nodes': [],
            'warning_nodes': [],
            'danger_nodes': []
          };
        }
        fabscript_node_map[script_name]['links'].push(index);
      }
      index++;
    }
    graph_nodes = [];
    graph_links = [];
    _results = [];
    for (fabscript in fabscript_node_map) {
      fabscript_node = fabscript_node_map[fabscript];
      success_length = fabscript_node.success_nodes.length;
      warning_length = fabscript_node.warning_nodes.length;
      danger_length = fabscript_node.danger_nodes.length;
      graph_nodes[fabscript_node.index] = {
        name: fabscript,
        icon: fabscript_node.icon,
        success_length: success_length,
        warning_length: warning_length,
        danger_length: danger_length
      };
      _results.push((function() {
        var _len4, _n, _ref2, _results1;
        _ref2 = fabscript_node.links;
        _results1 = [];
        for (_n = 0, _len4 = _ref2.length; _n < _len4; _n++) {
          link = _ref2[_n];
          _results1.push(graph_links.push({
            'source': fabscript_node.index,
            'target': link
          }));
        }
        return _results1;
      })());
    }
    return _results;
  };

  render_all = function() {
    if (mode.current === mode.USER) {
      render_user();
    } else if (mode.current === mode.FABSCRIPT) {
      render_fabscript();
    } else if (mode.current === mode.RESULT) {
      render_result();
    } else if (mode.current === mode.NODE) {
      render_node();
    }
    return $('[data-toggle=popover]').popover();
  };

  init = function() {
    var fabscript, _i, _len;
    $('#show-graph').on('click', function() {
      $('#graph-modal').modal();
    });
    $('#graph-modal').on('shown.bs.modal', function() {
      render_force_layout();
    });
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
    nodes = $('#nodes');
    if (nodes.length > 0) {
      mode.current = mode.NODE;
      nodes = JSON.parse(nodes.html());
    }
    node_clusters = $('#node_clusters');
    if (node_clusters.length > 0) {
      node_clusters = JSON.parse(node_clusters.html());
    }
    fabscripts = $('#fabscripts');
    if (fabscripts.length > 0) {
      mode.current = mode.FABSCRIPT;
      fabscripts = JSON.parse(fabscripts.html());
      for (_i = 0, _len = fabscripts.length; _i < _len; _i++) {
        fabscript = fabscripts[_i];
        fabscript.fields.data = JSON.parse(fabscript.fields.data);
        fabscript.fields.link = JSON.parse(fabscript.fields.link);
        fabscript.fields.linked_fabscripts = JSON.parse(fabscript.fields.linked_fabscripts);
      }
    }
    results = $('#results');
    if (results.length > 0) {
      mode.current = mode.RESULT;
      results = JSON.parse(results.html());
    }
    render_all();
  };

  init();

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
      init();
    });
  }

  $(window).on('hashchange', function() {
    render_all();
  });

}).call(this);
