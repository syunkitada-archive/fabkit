render_node_cluster = ->
    fabscript_node_map = {}

    node_cluster.datamap.status = {'type': 'svg'}
    node_cluster.datamap.relation = {'type': 'svg'}
    node_map = node_cluster.__status.node_map
    fabscript_map = node_cluster.__status.fabscript_map

    nodes_tbody_html = ''
    all_node_length = 0
    success_node_length = 0
    warning_node_length = 0
    danger_node_length = 0
    for host, node of node_map
        all_node_length++
        is_warning = false
        is_danger = false

        sum_status = 0
        result_html = '<div>'
        for script, result of node.fabscript_map
            sum_status += result.task_status + result.check_status
            result_html += """
            #{script} [#{result.task_status}],
            setup [#{result.status}]: '#{result.msg}',
            check [#{result.check_status}]: '#{result.check_msg}'
            </tr>
            """
            if result.task_status > 0 or result.check_status > 0
                if result.task_status < WARNING_STATUS_THRESHOLD or result.check_status < WARNING_STATUS_THRESHOLD
                    is_warning = true
                else
                    is_danger = true

        if is_danger
            node_class = 'danger'
            danger_node_length++
        else if is_warning
            node_class = 'warning'
            warning_node_length++
        else
            node_class = ''
            success_node_length++

        result_html += '</div>'
        nodes_tbody_html += """
            <tr class="#{node_class}">
                <td>#{sum_status}</td>
                <td>#{host}</td>
                <td>#{result_html}</td>
            </tr>"""

    console.log node_map
    $('#all-node-badge').html(all_node_length)
    $('#success-node-badge').html(success_node_length)
    $('#warning-node-badge').html(warning_node_length)
    $('#danger-node-badge').html(danger_node_length)
    $('#nodes-tbody').html(nodes_tbody_html)
#
#    $('#all-node-badge').html(all_node_length)
#
#    results_tbody_html = ''
#    all_node_length = nodes.length
#    success_node_length = 0
#    warning_node_length = 0
#    danger_node_length = 0
#    for result, i in nodes
#        if result.fields.status == 0
#            success_node_length++
#        else if result.fields.status < WARNING_STATUS_THRESHOLD
#            warning_node_length++
#        else
#            danger_node_length++
#
#        tmp_logs_html = ''
#        i = 0
#        for fabscript, log of JSON.parse(result.fields.logs)
#            node = {
#                type: 'node',
#                'index': i,
#                'name': result.fields.path,
#                'size': 1,
#            }
#            i++
#
#            if fabscript not of fabscript_node_map
#                fabscript_node_map[fabscript] = {
#                    'links': [],
#                    'success_nodes': [],
#                    'warning_nodes': [],
#                    'danger_nodes': [],
#                }
#
#            if log.status == 0
#                node['class'] = 'success'
#                fabscript_node_map[fabscript]['success_nodes'].push(node)
#            else if log.status < WARNING_STATUS_THRESHOLD
#                node['class'] = 'warning'
#                fabscript_node_map[fabscript]['warning_nodes'].push(node)
#            else
#                node['class'] = 'danger'
#                fabscript_node_map[fabscript]['danger_nodes'].push(node)
#
#            tmp_logs_html += "#{fabscript} [#{log.status}]: #{log.msg}[#{log.task_status}]<br>"
#
#        logs_all_html = ''
#        logs_all = JSON.parse(result.fields.logs_all)
#        if logs_all.length == 0
#            logs_all_html = 'No data'
#        else
#            for log in logs_all by -1
#                timestamp = new Date(log.timestamp * 1000)
#                logs_all_html += "#{log.fabscript}[#{log.status}]: #{log.msg}[#{log.task_status}] #{timestamp}<br>"
#
#        logs_html = """
#            <a class="popover-anchor" data-containe="body" data-toggle="popover"
#                data-placement="bottom" data-html="true" data-title="Logs all" data-content="#{logs_all_html}">
#                #{tmp_logs_html}
#            </a>"""
#
#        if result.fields.status == 0
#            tr_class = ''
#        else if result.fields.status < WARNING_STATUS_THRESHOLD
#            tr_class = 'warning'
#        else
#            tr_class = 'danger'
#
#        results_tbody_html += "
#            <tr id=\"#{result.pk}\" class=\"#{tr_class}\">
#                <td><input type=\"checkbox\"></td>
#                <td>#{result.fields.path}</td>
#                <td>#{result.fields.status}</td>
#                <td>#{result.fields.msg}</td>
#                <td>#{logs_html}</td>
#                <td>#{result.fields.updated_at}</td>
#            </tr>"
#
#    $('#nodes-tbody').html(results_tbody_html)
#
#    $('#all-node-badge').html(all_node_length)
#    $('#success-node-badge').html(success_node_length)
#    $('#warning-node-badge').html(warning_node_length)
#    $('#danger-node-badge').html(danger_node_length)
#
#    index = 0
#    for fabscript in fabscripts
#        name = fabscript.fields.name
#        if name not of fabscript_node_map
#            continue
#
#        fabscript_node_map[name].index = index
#
#        if 'icon' of fabscript.fields.data
#            fabscript_node_map[name].icon = fabscript.fields.data.icon
#        else
#            fabscript_node_map[name].icon = 'computer-retro'
#
#        for linked_fabscript in fabscript.fields.linked_fabscripts
#            script_name = linked_fabscript.split(':')[0]
#
#            if script_name not of fabscript_node_map
#                fabscript_node_map[script_name] = {
#                    'links': [],
#                    'success_nodes': [],
#                    'warning_nodes': [],
#                    'danger_nodes': [],
#                }
#
#            fabscript_node_map[script_name]['links'].push(index)
#
#        index++
#
#    graph_nodes = []
#    graph_links = []
#    for fabscript, fabscript_node of fabscript_node_map
#        success_nodes = fabscript_node.success_nodes
#        warning_nodes = fabscript_node.warning_nodes
#        danger_nodes = fabscript_node.danger_nodes
#        success_length = success_nodes.length
#        warning_length = warning_nodes.length
#        danger_length = danger_nodes.length
#        graph_nodes[fabscript_node.index] = {
#            type: 'fabscript',
#            name: fabscript,
#            icon: fabscript_node.icon,
#            success_length: success_length,
#            warning_length: warning_length,
#            danger_length: danger_length,
#            children: [
#                {
#                    type: 'status',
#                    name: 'success',
#                    class: 'success',
#                    length: success_length,
#                    children: success_nodes,
#                }, {
#                    type: 'status',
#                    name: 'warning',
#                    class: 'warning',
#                    length: warning_length,
#                    children: warning_nodes,
#                }, {
#                    type: 'status',
#                    name: 'danger',
#                    class: 'danger',
#                    length: danger_length,
#                    children: danger_nodes,
#                }
#            ]
#        }
#
#        for link in fabscript_node.links
#            graph_links.push({
#                'source': fabscript_node.index,
#                'target': link,
#            })
