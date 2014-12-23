(function() {
  var render_fabscripts, render_nodes, render_results;

  if ($.support.pjax) {
    $(document).pjax('.pjax', '#pjax-container');
    $(document).on('pjax:end', function() {
      $('.pjax').parent().removeClass('active');
      $('a[href="' + location.pathname + '"]').parent().addClass('active');
      render_fabscripts();
      render_nodes();
      return render_results();
    });
  }

  render_fabscripts = function() {
    var active, cluster, cluster_data, clusters_html, connected, connected_html, fabscript_cluster_map, fabscripts, fabscripts_tbody, hash, script, scripts, _i, _j, _len, _len1, _ref;
    fabscripts = $('#fabscripts');
    fabscripts_tbody = $('#fabscripts-tbody');
    if (fabscripts_tbody.length > 0) {
      scripts = JSON.parse(fabscripts.html());
      fabscript_cluster_map = {
        'all': scripts
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      fabscripts_tbody.empty();
      for (_i = 0, _len = scripts.length; _i < _len; _i++) {
        script = scripts[_i];
        script.fields.connection = JSON.parse(script.fields.connection);
        script.fields.connected_fabscripts = JSON.parse(script.fields.connected_fabscripts);
        connected_html = '';
        _ref = script.fields.connected_fabscripts;
        for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
          connected = _ref[_j];
          connected_html += "" + connected + "</br>";
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
          fabscripts_tbody.append("<tr> <td>" + script.fields.name + "</td> <td>" + connected_html + "</td> <td>" + script.fields.updated_at + "</td> </tr>");
        }
      }
      clusters_html = '';
      for (cluster in fabscript_cluster_map) {
        scripts = fabscript_cluster_map[cluster];
        active = "";
        if (hash === ("#" + cluster)) {
          active = "active";
        }
        clusters_html += "<li class=\"" + active + "\"><a href=\"#" + cluster + "\">" + cluster + " (" + scripts.length + ")</a></li>";
      }
      return $('#fabscript-clusters').html(clusters_html);
    }
  };

  render_nodes = function() {
    var active, cluster, cluster_data, clusters_html, hash, node, node_cluster_map, nodes, nodes_tbody, _i, _len;
    nodes = $('#nodes');
    nodes_tbody = $('#nodes-tbody');
    if (nodes_tbody.length > 0) {
      nodes = JSON.parse(nodes.html());
      node_cluster_map = {
        'all': nodes
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      nodes_tbody.empty();
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
          nodes_tbody.append("<tr> <td>" + node.fields.path + "</td> <td>" + node.fields.host + "</td> <td>" + node.fields.ip + "</td> <td>" + node.fields.uptime + "</td> <td>" + node.fields.ssh + "</td> </tr>");
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
      return $('#node-clusters').html(clusters_html);
    }
  };

  render_results = function() {
    var active, cluster, cluster_data, clusters_html, hash, i, id_logs, log, logs_all_html, logs_html, nodes, result, result_cluster_map, results, results_tbody, timestamp, tmp_logs_html, _i, _j, _k, _len, _len1, _len2, _ref, _ref1;
    results = $('#results');
    nodes = $('#nodes');
    results_tbody = $('#results-tbody');
    if (results_tbody.length > 0) {
      results = JSON.parse(results.html());
      result_cluster_map = {
        'all': results
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      results_tbody.empty();
      for (i = _i = 0, _len = results.length; _i < _len; i = ++_i) {
        result = results[i];
        cluster = result.fields.node_path.split('/')[0];
        if (cluster in result_cluster_map) {
          cluster_data = result_cluster_map[cluster];
          cluster_data.push(result);
        } else {
          cluster_data = [result];
        }
        tmp_logs_html = '';
        _ref = JSON.parse(result.fields.logs);
        for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
          log = _ref[_j];
          tmp_logs_html += "" + log.fabscript + ": " + log.msg + "[" + log.status + "]<br>";
        }
        logs_all_html = '';
        _ref1 = JSON.parse(result.fields.logs_all);
        for (_k = 0, _len2 = _ref1.length; _k < _len2; _k++) {
          log = _ref1[_k];
          timestamp = new Date(log.timestamp * 1000);
          logs_all_html += "" + log.fabscript + ": " + log.msg + "[" + log.status + "] " + timestamp + "<br>";
        }
        id_logs = "log_" + i;
        result_cluster_map[cluster] = cluster_data;
        logs_html = "<a class=\"\" data-toggle=\"collapse\" data-target=\"#" + id_logs + "\" aria-expanded=\"true\" aria-controls=\"" + id_logs + "\">\n    " + tmp_logs_html + "\n</a>\n\n<div id=\"" + id_logs + "\" class=\"collapse\">\n" + logs_all_html + "\n</div>";
        if (hash === '#all' || hash === ("#" + cluster)) {
          results_tbody.append("<tr> <td>" + result.fields.node_path + "</td> <td>" + result.fields.status + "</td> <td>" + result.fields.msg + "</td> <td>" + logs_html + "</td> <td>" + result.fields.updated_at + "</td> </tr>");
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
      return $('#result-clusters').html(clusters_html);
    }
  };

  render_fabscripts();

  render_nodes();

  render_results();

  $(window).on('hashchange', function() {
    render_fabscripts();
    render_nodes();
    render_results();
  });

}).call(this);

(function() {
  var force, h, link, links, node, nodes, svg, w;

  w = 400;

  h = 400;

  nodes = [
    {
      'name': 'graphite-web'
    }, {
      'name': 'mysql'
    }, {
      'name': 'carbon-relay'
    }, {
      'name': 'carbon-cache'
    }
  ];

  links = [
    {
      'source': 0,
      'target': 1
    }
  ];

  svg = d3.select("#render").attr("width", w).attr("height", h);

  force = d3.layout.force().nodes(nodes).links(links).gravity(.05).distance(100).charge(-100).size([w, h]);

  link = svg.selectAll('.link').data(links).enter().append('line').attr('class', 'link');

  node = svg.selectAll(".node").data(nodes).enter().append('g').attr('class', 'node').call(force.drag);

  node.append("circle").attr("r", 5).style("fill", "green");

  node.append('text').attr('dx', 12).attr('dy', '.35em').text(function(d) {
    return d.name;
  });

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

  force.start();

}).call(this);
