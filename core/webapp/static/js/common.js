(function() {
  var render_fabscripts, render_nodes, render_results;

  console.log('test');

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
        connected_html = '<ul>';
        _ref = script.fields.connected_fabscripts;
        for (_j = 0, _len1 = _ref.length; _j < _len1; _j++) {
          connected = _ref[_j];
          connected_html += "<li>" + connected + "</li>";
        }
        connected_html += '</ul>';
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
      console.log(clusters_html);
      return $('#fabscript-clusters').html(clusters_html);
    }
  };

  render_nodes = function() {
    var active, cluster, cluster_data, clusters_html, hash, node, node_cluster_map, nodes, nodes_tbody, _i, _len;
    nodes = $('#nodes');
    nodes_tbody = $('#nodes-tbody');
    if (nodes_tbody.length > 0) {
      nodes = JSON.parse(nodes.html());
      console.log(nodes);
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
      console.log(clusters_html);
      return $('#node-clusters').html(clusters_html);
    }
  };

  render_results = function() {
    var active, cluster, cluster_data, clusters_html, hash, nodes, result, result_cluster_map, results, results_tbody, _i, _len;
    results = $('#results');
    nodes = $('#nodes');
    results_tbody = $('#results-tbody');
    console.log(results);
    if (results_tbody.length > 0) {
      results = JSON.parse(results.html());
      console.log(results);
      result_cluster_map = {
        'all': results
      };
      hash = location.hash;
      if (hash === '') {
        hash = '#all';
      }
      results_tbody.empty();
      for (_i = 0, _len = results.length; _i < _len; _i++) {
        result = results[_i];
        cluster = result.fields.node_path.split('/')[0];
        if (cluster in result_cluster_map) {
          cluster_data = result_cluster_map[cluster];
          cluster_data.push(result);
        } else {
          cluster_data = [result];
        }
        result_cluster_map[cluster] = cluster_data;
        if (hash === '#all' || hash === ("#" + cluster)) {
          results_tbody.append("<tr> <td>" + result.fields.node_path + "</td> <td>" + result.fields.status + "</td> <td>" + result.fields.msg + "</td> <td>" + result.fields.logs + "</td> <td>" + result.fields.logs_all + "</td> <td>" + result.fields.updated_at + "</td> </tr>");
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
      console.log(clusters_html);
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
