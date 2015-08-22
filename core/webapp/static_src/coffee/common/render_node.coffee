render_node_cluster = ->
    fabscript_node_map = {}

    node_map = node_cluster.__status.node_map
    fabscript_map = node_cluster.__status.fabscript_map
    for fabscript, data of fabscript_map
        data.children = [
            {type: 'status', name: 'success', class: 'success', length: 0, children: []},
            {type: 'status', name: 'warning', class: 'warning', length: 0, children: []},
            {type: 'status', name: 'danger', class: 'danger', length: 0, children: []},
        ]

    fabscripts = []

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
            <br>
            """

            node = {'type': node, 'name': host, 'size': 1}
            if result.task_status > 0 or result.check_status > 0
                if result.task_status < WARNING_STATUS_THRESHOLD or result.check_status < WARNING_STATUS_THRESHOLD
                    is_warning = true
                    tmp_fabscript = fabscript_map[script].children[1]
                else
                    is_danger = true
                    tmp_fabscript = fabscript_map[script].children[2]
            else
                tmp_fabscript = fabscript_map[script].children[0]

            tmp_fabscript.children.push(node)
            tmp_fabscript.length++

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

    $('#all-node-badge').html(all_node_length)
    $('#success-node-badge').html(success_node_length)
    $('#warning-node-badge').html(warning_node_length)
    $('#danger-node-badge').html(danger_node_length)
    $('#nodes-tbody').html(nodes_tbody_html)

    fabscript_status_map = []
    for fabscript, data of fabscript_map
        data.name = fabscript
        data.type = 'fabscript'
        data.success_length = data.children[0].length
        data.warning_length = data.children[1].length
        data.danger_length = data.children[2].length

        fabscript_status_map.push({
            '!!fabscript': fabscript,
            '!0success': data.success_length,
            '!1warning': data.warning_length,
            '!2danger': data.danger_length,
        })

    node_cluster.datamap.status = {
        'name': 'status',
        'type': 'table',
        'data': fabscript_status_map,
    }


    nodes = []
    links = []
    index = 0
    for name, fabscript of fabscript_map
        fabscript.icon = 'computer-retro'
        fabscript.index = index
        nodes.push(fabscript)
        index++

    for node, i in nodes
        for require, status of node.require
            if require of fabscript_map
                target = fabscript_map[require].index
            else
                target = nodes.length
                fabscript = {
                    name: require,
                    icon: 'computer-retro',
                    index: target,
                }
                nodes.push(fabscript)
                fabscript_map[require] = fabscript

            links.push({
                'source': i,
                'target': target,
            })

    node_cluster.datamap.relation = {
        'name': 'relation',
        'type': 'force'
        'data': {
            'nodes': nodes,
            'links': links,
        }
    }
