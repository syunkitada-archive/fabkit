(function() {
  var WARNING_STATUS_THRESHOLD, bind_shown_tab_event, datamap_tabs, fabscripts, filter, graph_links, graph_nodes, init, mode, node_cluster, node_clusters, render_all, render_datamap, render_map, render_node_cluster, render_node_clusters, render_partition_panel, render_table_panel, render_user, users,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.fabkit = {};

  users = [];

  node_cluster = {};

  node_clusters = [];

  fabscripts = [];

  datamap_tabs = ['status'];

  graph_links = [];

  graph_nodes = [];

  mode = {
    current: 0,
    USER: 0,
    NODE: 1
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

  render_partition_panel = function(panel_id, map) {
    var $svg, click, g, h, id, kx, ky, links, nodes, partition, root, svg, transform, vis, w, x, y;
    id = 'partition-svg';
    root = map.data;
    $("#" + panel_id).html("<div class=\"graph-svg-wrapper\">\n    <svg id=\"" + id + "\"></svg>\n</div>");
    id = '#partition-svg';
    nodes = graph_nodes;
    links = graph_links;
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
        map.is_rendered = true;
        if (map.type === 'table') {
          render_table_panel(panel_id, map);
        }
        if (map.type === 'partition') {
          render_partition_panel(panel_id, map);
        }
      }
    });
  };

  render_map = function() {
    return console.log('test');
  };

  render_table_panel = function(panel_id, map) {
    var host, index, table_html, tbody_html, td, tds, th, thead_html, ths, tr, _i, _len, _ref;
    thead_html = '<tr>';
    console.log(map);
    thead_html = '<th>host</th>';
    ths = [];
    tbody_html = '';
    _ref = map.data;
    for (host in _ref) {
      tr = _ref[host];
      tds = [];
      for (th in tr) {
        td = tr[th];
        index = ths.indexOf(th);
        if (index === -1) {
          thead_html += "<th>" + th + "</th>";
          ths.push(th);
          index = ths.length - 1;
        }
        tds[index] = td;
      }
      tbody_html += '<tr>';
      tbody_html += "<td>" + host + "</td>";
      for (_i = 0, _len = tds.length; _i < _len; _i++) {
        td = tds[_i];
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

  render_node_clusters = function() {
    var cluster_path, clusters_html, expand_clusters, page, paths;
    paths = location.pathname.split('node/');
    page = 'node';
    cluster_path = paths[1].slice(0, -1);
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
    expand_clusters(clusters_html, node_clusters, null);
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
    var all_node_length, danger_node_length, data, fabscript, fabscript_map, fabscript_node_map, host, is_danger, is_warning, node, node_class, node_map, nodes_tbody_html, result, result_html, script, success_node_length, sum_status, tmp_fabscript, warning_node_length, _ref;
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
    console.log(fabscript_map);
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
        result_html += "" + script + " [" + result.task_status + "],\nsetup [" + result.status + "]: '" + result.msg + "',\ncheck [" + result.check_status + "]: '" + result.check_msg + "'\n</tr>";
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
    console.log('DEBUG DD');
    fabscripts = [];
    for (fabscript in fabscript_map) {
      data = fabscript_map[fabscript];
      console.log(fabscript);
      console.log(data);
      data.name = fabscript;
      data.type = 'fabscript';
      data.success_length = data.children[0].length;
      data.warning_length = data.children[1].length;
      data.danger_length = data.children[2].length;
      fabscripts.push(data);
    }
    $('#all-node-badge').html(all_node_length);
    $('#success-node-badge').html(success_node_length);
    $('#warning-node-badge').html(warning_node_length);
    $('#danger-node-badge').html(danger_node_length);
    $('#nodes-tbody').html(nodes_tbody_html);
    node_cluster.datamap.status = {
      'name': 'status',
      'type': 'partition',
      'data': {
        type: 'root',
        name: 'status',
        children: fabscripts
      }
    };
    console.log('DEBUG 22');
    return console.log(node_cluster.datamap.status.data);
  };

  render_all = function() {
    if (mode.current === mode.USER) {
      render_user();
    } else if (mode.current === mode.NODE) {
      render_node_clusters();
      render_node_cluster();
      $('#node-table').tablesorter({
        sortList: [[0, 1], [1, 0]]
      });
      console.log('DEBUG');
      console.log(node_cluster);
      console.log(fabscripts);
      $('#show-datamap').on('click', function() {
        $('#datamap-modal').modal();
      });
      render_datamap();
      $('#datamap-modal').on('shown.bs.modal', function() {
        $('#map-df').tab('show');
      });
      bind_shown_tab_event();
      $('#show-datamap').click();
    }
    return $('[data-toggle=popover]').popover();
  };

  init = function() {
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
    if (location.hash !== '') {
      render_all();
    }
  });

}).call(this);
