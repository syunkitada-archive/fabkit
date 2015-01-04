render_result = ->
    render_node_clusters()

    fabscript_node_map = {}

    results_tbody_html = ''
    for result, i in results
        tmp_logs_html = ''
        for log in JSON.parse(result.fields.logs)
            node = {
                'index': i,
                'name': result.fields.node_path,
            }

            if log.fabscript not of fabscript_node_map
                fabscript_node_map[log.fabscript] = {
                    'links': [],
                    'success_nodes': [],
                    'warning_nodes': [],
                    'danger_nodes': [],
                }

            if log.status == 0
                fabscript_node_map[log.fabscript]['success_nodes'].push(node)
            else if log.status < WARNING_STATUS_THRESHOLD
                fabscript_node_map[log.fabscript]['warning_nodes'].push(node)
            else
                fabscript_node_map[log.fabscript]['danger_nodes'].push(node)

            tmp_logs_html += "#{log.fabscript}: #{log.msg}[#{log.status}]<br>"

        logs_all_html = ''
        logs_all = JSON.parse(result.fields.logs_all)
        if logs_all.length == 0
            logs_all_html = 'No data'
        else
            for log in logs_all
                timestamp = new Date(log.timestamp * 1000)
                logs_all_html += "#{log.fabscript}: #{log.msg}[#{log.status}] #{timestamp}<br>"

        logs_html = """
            <a class="popover-anchor" data-containe="body" data-toggle="popover"
                data-placement="bottom" data-html="true" data-title="Logs all" data-content="#{logs_all_html}">
                #{tmp_logs_html}
            </a>"""

        if result.fields.status == 0
            tr_class = ''
        else if result.fields.status < WARNING_STATUS_THRESHOLD
            tr_class = 'warning'
        else
            tr_class = 'danger'

        results_tbody_html += "
            <tr id=\"#{result.pk}\" class=\"#{tr_class}\">
                <td><input type=\"checkbox\"></td>
                <td>#{result.fields.node_path}</td>
                <td>#{result.fields.status}</td>
                <td>#{result.fields.msg}</td>
                <td>#{logs_html}</td>
                <td>#{result.fields.updated_at}</td>
            </tr>"

    $('#results-tbody').html(results_tbody_html)

    index = 0
    for fabscript in fabscripts
        name = fabscript.fields.name
        if name not of fabscript_node_map
            continue

        fabscript_node_map[name].index = index

        if 'icon' of fabscript.fields.data
            fabscript_node_map[name].icon = fabscript.fields.data.icon
        else
            fabscript_node_map[name].icon = 'computer-retro'

        for linked_fabscript in fabscript.fields.linked_fabscripts
            script_name = linked_fabscript.split(':')[0]
            fabscript_node_map[script_name]['links'].push(index)

        index++

    graph_nodes = []
    graph_links = []
    for fabscript, fabscript_node of fabscript_node_map
        success_length = fabscript_node.success_nodes.length
        warning_length = fabscript_node.warning_nodes.length
        danger_length = fabscript_node.danger_nodes.length
        graph_nodes[fabscript_node.index] = {
            name: fabscript,
            icon: fabscript_node.icon,
            success_length: success_length,
            warning_length: warning_length,
            danger_length: danger_length,
        }

        for link in fabscript_node.links
            graph_links.push({
                'source': fabscript_node.index,
                'target': link,
            })
