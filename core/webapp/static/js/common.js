(function() {
  var fabscripts, filter, graph_links, graph_nodes, init, mode, nodes, render_all, render_fabscript, render_force_layout, render_node, render_result, render_user, results, users,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.fabkit = {};

  users = [];

  nodes = [];

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
    node.append("image").attr("xlink:href", "/static/vendor/defaulticon/png/computer-retro.png").attr("x", 6).attr("y", -34).attr('width', 30).attr('height', 30);
    node.append("circle").attr("r", 6).attr('class', 'node-circle');
    node.append('text').attr('dx', 12).attr('dy', '.35em').attr('class', 'node-label').text(function(d) {
      return d.name;
    });
    if (mode.current === mode.RESULT) {
      node.append('text').attr('dx', 12).attr('dy', '.35em').attr('y', 16).attr('class', function(d) {
        if (d.failed_length > 0) {
          return 'node-label-failed';
        } else {
          return 'node-label-success';
        }
      }).text(function(d) {
        return "success (" + d.success_length + "), failed (" + d.failed_length + ")";
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
    var active, cluster, cluster_data, clusters_html, fabscript, fabscript_cluster_map, fabscripts_tbody, hash, i, is_exist, linked, linked_html, linked_index, node, node_index, node_map, script, _i, _j, _k, _l, _len, _len1, _len2, _len3, _len4, _m, _ref, _ref1;
    fabscripts_tbody = $('#fabscripts-tbody');
    if (fabscripts_tbody.length > 0) {
      node_map = {};
      graph_nodes = [];
      graph_links = [];
      fabscript_cluster_map = {
        'all': fabscripts
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      fabscripts_tbody.empty();
      for (_i = 0, _len = fabscripts.length; _i < _len; _i++) {
        script = fabscripts[_i];
        linked_html = '';
        _ref = script.fields.linked_fabscripts;
        for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
          linked = _ref[_j];
          linked_html += "" + linked + "</br>";
        }
        cluster = script.fields.name.split('.')[0];
        if (cluster in fabscript_cluster_map) {
          cluster_data = fabscript_cluster_map[cluster];
          cluster_data.push(script);
        } else {
          cluster_data = [script];
        }
        fabscript_cluster_map[cluster] = cluster_data;
        if (hash === '#all' || hash === ("#" + cluster)) {
          fabscripts_tbody.append("<tr id=\"" + script.pk + "\"> <td><input type=\"checkbox\"></td> <td>" + script.fields.name + "</td> <td>" + linked_html + "</td> <td>" + script.fields.updated_at + "</td> </tr>");
          if (hash !== "#all") {
            is_exist = false;
            node_index = 0;
            for (i = _k = 0, _len2 = graph_nodes.length; _k < _len2; i = ++_k) {
              node = graph_nodes[i];
              if (node.name === script.fields.name) {
                is_exist = true;
                node_index = i;
                break;
              }
            }
            if (!is_exist) {
              node_index = graph_nodes.length;
              graph_nodes.push({
                'name': script.fields.name
              });
            }
            _ref1 = script.fields.linked_fabscripts;
            for (_l = 0, _len3 = _ref1.length; _l < _len3; _l++) {
              fabscript = _ref1[_l];
              fabscript = fabscript.split(':')[0];
              is_exist = false;
              linked_index = 0;
              for (i = _m = 0, _len4 = graph_nodes.length; _m < _len4; i = ++_m) {
                node = graph_nodes[i];
                if (node.name === fabscript) {
                  is_exist = true;
                  linked_index = i;
                  break;
                }
              }
              if (!is_exist) {
                linked_index = graph_nodes.length;
                graph_nodes.push({
                  'name': fabscript
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
      clusters_html = '';
      for (cluster in fabscript_cluster_map) {
        fabscripts = fabscript_cluster_map[cluster];
        active = "";
        if (hash === ("#" + cluster)) {
          active = "active";
        }
        clusters_html += "<li class=\"" + active + "\"><a href=\"#" + cluster + "\">" + cluster + " (" + fabscripts.length + ")</a></li>";
      }
      $('#fabscript-clusters').html(clusters_html);
      if (hash === '#all') {
        return $('#show-graph').hide();
      } else {
        return $('#show-graph').show();
      }
    }
  };

  render_node = function() {
    var active, cluster, cluster_data, clusters_html, hash, node, node_cluster_map, node_clusters, nodes_tbody, _i, _len;
    nodes_tbody = $('#nodes-tbody');
    node_clusters = $('#node-clusters');
    if (nodes_tbody.length > 0) {
      node_cluster_map = {
        'all': nodes
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      nodes_tbody.empty();
      node_clusters.empty();
      for (_i = 0, _len = nodes.length; _i < _len; _i++) {
        node = nodes[_i];
        cluster = node.fields.path.split('/')[0];
        if (cluster in node_cluster_map) {
          cluster_data = node_cluster_map[cluster];
          cluster_data.push(node);
        } else {
          cluster_data = [node];
        }
        node_cluster_map[cluster] = cluster_data;
        if (hash === '#all' || hash === ("#" + cluster)) {
          nodes_tbody.append("<tr id=\"" + node.pk + "\"> <td><input type=\"checkbox\"></td> <td>" + node.fields.path + "</td> <td>" + node.fields.host + "</td> <td>" + node.fields.ip + "</td> <td>" + node.fields.uptime + "</td> <td>" + node.fields.ssh + "</td> </tr>");
        }
      }
      clusters_html = '';
      for (cluster in node_cluster_map) {
        nodes = node_cluster_map[cluster];
        active = "";
        if (hash === ("#" + cluster)) {
          active = "active";
        }
        clusters_html += "<li class=\"" + active + "\"><a href=\"#" + cluster + "\">" + cluster + " (" + nodes.length + ")</a></li>";
      }
      return node_clusters.html(clusters_html);
    }
  };

  render_result = function() {
    var active, cluster, cluster_data, clusters_html, current_index, fabscript, fabscript_node, fabscript_node_map, hash, i, id_logs, index, link, log, logs_all_html, logs_html, name, node, result, result_cluster_map, result_node_map, results_tbody, script, timestamp, tmp_logs_html, _i, _j, _k, _l, _len, _len1, _len2, _len3, _len4, _len5, _m, _n, _ref, _ref1, _ref2, _ref3;
    results_tbody = $('#results-tbody');
    if (results_tbody.length > 0) {
      result_cluster_map = {
        'all': results
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      fabscript_node_map = {};
      result_node_map = {};
      if (hash === '#all') {
        $('#show-graph').hide();
      } else {
        $('#show-graph').show();
        console.log('DEBUG');
        console.log(fabscripts);
        index = 0;
        for (_i = 0, _len = fabscripts.length; _i < _len; _i++) {
          script = fabscripts[_i];
          name = script.fields.name;
          if (!(name in fabscript_node_map)) {
            fabscript_node_map[name] = {
              'links': [],
              'success_nodes': [],
              'failed_nodes': [],
              'index': index
            };
            current_index = index;
            index++;
          } else {
            current_index = fabscript_node_map[name]['index'];
          }
          _ref = script.fields.linked_fabscripts;
          for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
            fabscript = _ref[_j];
            fabscript = fabscript.split(':')[0];
            if (!(fabscript in fabscript_node_map)) {
              fabscript_node_map[fabscript] = {
                'links': [current_index],
                'success_nodes': [],
                'failed_nodes': [],
                'index': index
              };
              index++;
            } else {
              fabscript_node_map[fabscript]['links'].push(current_index);
            }
          }
        }
      }
      console.log(fabscript_node_map);
      results_tbody.empty();
      for (i = _k = 0, _len2 = results.length; _k < _len2; i = ++_k) {
        result = results[i];
        cluster = result.fields.node_path.split('/')[0];
        if (cluster in result_cluster_map) {
          cluster_data = result_cluster_map[cluster];
          cluster_data.push(result);
        } else {
          cluster_data = [result];
        }
        tmp_logs_html = '';
        _ref1 = JSON.parse(result.fields.logs);
        for (_l = 0, _len3 = _ref1.length; _l < _len3; _l++) {
          log = _ref1[_l];
          if (hash !== '#all') {
            node = {
              'index': i,
              'name': result.fields.node_path
            };
            if (log.status === 0) {
              fabscript_node_map[log.fabscript]['success_nodes'].push(node);
            } else {
              fabscript_node_map[log.fabscript]['failed_nodes'].push(node);
            }
          }
          tmp_logs_html += "" + log.fabscript + ": " + log.msg + "[" + log.status + "]<br>";
        }
        logs_all_html = '';
        _ref2 = JSON.parse(result.fields.logs_all);
        for (_m = 0, _len4 = _ref2.length; _m < _len4; _m++) {
          log = _ref2[_m];
          timestamp = new Date(log.timestamp * 1000);
          logs_all_html += "" + log.fabscript + ": " + log.msg + "[" + log.status + "] " + timestamp + "<br>";
        }
        id_logs = "log_" + i;
        result_cluster_map[cluster] = cluster_data;
        logs_html = "<a class=\"popover-anchor\" data-containe=\"body\" data-toggle=\"popover\" data-placement=\"bottom\" data-html=\"true\" data-content=\"" + logs_all_html + "\">\n    " + tmp_logs_html + "\n </a>";
        if (hash === '#all' || hash === ("#" + cluster)) {
          results_tbody.append("<tr id=\"" + result.pk + "\"> <td><input type=\"checkbox\"></td> <td>" + result.fields.node_path + "</td> <td>" + result.fields.status + "</td> <td>" + result.fields.msg + "</td> <td>" + logs_html + "</td> <td>" + result.fields.updated_at + "</td> </tr>");
        }
      }
      clusters_html = '';
      for (cluster in result_cluster_map) {
        results = result_cluster_map[cluster];
        active = "";
        if (hash === ("#" + cluster)) {
          active = "active";
        }
        clusters_html += "<li class=\"" + active + "\"><a href=\"#" + cluster + "\">" + cluster + " (" + results.length + ")</a></li>";
      }
      $('#result-clusters').html(clusters_html);
      graph_nodes = [];
      graph_links = [];
      for (fabscript in fabscript_node_map) {
        fabscript_node = fabscript_node_map[fabscript];
        graph_nodes[fabscript_node.index] = {
          name: fabscript,
          success_length: fabscript_node.success_nodes.length,
          failed_length: fabscript_node.failed_nodes.length
        };
        _ref3 = fabscript_node.links;
        for (_n = 0, _len5 = _ref3.length; _n < _len5; _n++) {
          link = _ref3[_n];
          graph_links.push({
            'source': fabscript_node.index,
            'target': link
          });
        }
      }
      console.log(graph_nodes);
      return console.log(graph_links);
    }
  };

  render_all = function() {
    render_user();
    render_fabscript();
    render_node();
    return render_result();
  };

  init = function() {
    var fabscript, _i, _len;
    $('[data-toggle=popover]').popover();
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
      console.log(nodes);
    }
    fabscripts = $('#fabscripts');
    if (fabscripts.length > 0) {
      mode.current = mode.FABSCRIPT;
      fabscripts = JSON.parse(fabscripts.html());
      for (_i = 0, _len = fabscripts.length; _i < _len; _i++) {
        fabscript = fabscripts[_i];
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

  if ($.support.pjax) {
    $(document).pjax('.pjax', '#pjax-container');
    $(document).on('pjax:end', function() {
      $('.pjax').parent().removeClass('active');
      $('a[href="' + location.pathname + '"]').parent().addClass('active');
      init();
    });
  }

  $(window).on('hashchange', function() {
    init();
  });

  init();

}).call(this);
