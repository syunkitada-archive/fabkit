(function() {
  var render_fabscripts;

  console.log('test');

  if ($.support.pjax) {
    $(document).pjax('.pjax', '#pjax-container');
    $(document).on('pjax:end', function() {
      $('.pjax').parent().removeClass('active');
      $('a[href="' + location.pathname + '"]').parent().addClass('active');
      return render_fabscripts();
    });
  }

  render_fabscripts = function() {
    var cluster, cluster_data, clusters_html, connected, connected_html, fabscript_cluster_map, fabscripts, fabscripts_tbody, script, scripts, _i, _j, _len, _len1, _ref;
    fabscripts = $('#fabscripts');
    fabscripts_tbody = $('#fabscripts-tbody');
    if (fabscripts.length > 0) {
      scripts = JSON.parse(fabscripts.html());
      fabscript_cluster_map = {};
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
        fabscripts_tbody.append("<tr> <td>" + script.fields.name + "</td> <td>" + connected_html + "</td> <td>" + script.fields.updated_at + "</td> </tr>");
        cluster = script.fields.name.split('.')[0];
        if (cluster in fabscript_cluster_map) {
          cluster_data = fabscript_cluster_map[cluster];
          cluster_data.push(script.fields.name);
        } else {
          cluster_data = [script.fields.name];
        }
        fabscript_cluster_map[cluster] = cluster_data;
      }
      console.log(fabscript_cluster_map);
      clusters_html = '';
      for (cluster in fabscript_cluster_map) {
        clusters_html += "<li><a href=\"#\">" + cluster + "</a></li>";
      }
      console.log(clusters_html);
      return $('#fabscript-clusters').html(clusters_html);
    }
  };

  render_fabscripts();

}).call(this);
