render_result = ->
    results_tbody = $('#results-tbody')
    if results_tbody.length > 0
        result_cluster_map = {'all': results}
        hash = location.hash
        if hash == ''
            hash = '#all'

        fabscript_node_map = {}
        result_node_map = {}
        if hash == '#all'
            $('#show-graph').hide()
        else
            $('#show-graph').show()

            console.log 'DEBUG'
            console.log fabscripts
            index = 0
            for script in fabscripts
                name = script.fields.name
                if name not of fabscript_node_map
                    fabscript_node_map[name] = {
                        'links': [],
                        'success_nodes': [],
                        'failed_nodes': [],
                        'index': index,
                    }
                    current_index = index
                    index++
                else
                    current_index = fabscript_node_map[name]['index']

                for fabscript in script.fields.linked_fabscripts
                    fabscript = fabscript.split(':')[0]
                    if fabscript not of fabscript_node_map
                        fabscript_node_map[fabscript] = {
                            'links': [current_index],
                            'success_nodes': [],
                            'failed_nodes': [],
                            'index': index
                        }
                        index++
                    else
                        fabscript_node_map[fabscript]['links'].push(current_index)
        console.log fabscript_node_map

        results_tbody.empty()
        for result, i in results
            cluster = result.fields.node_path.split('/')[0]
            if cluster of result_cluster_map
                cluster_data = result_cluster_map[cluster]
                cluster_data.push(result)
            else
                cluster_data = [result]

            tmp_logs_html = ''
            for log in JSON.parse(result.fields.logs)
                if hash != '#all'
                    node = {
                        'index': i,
                        'name': result.fields.node_path,
                    }

                    if log.status == 0
                        fabscript_node_map[log.fabscript]['success_nodes'].push(node)
                    else
                        fabscript_node_map[log.fabscript]['failed_nodes'].push(node)

                tmp_logs_html += "#{log.fabscript}: #{log.msg}[#{log.status}]<br>"

            logs_all_html = ''
            for log in JSON.parse(result.fields.logs_all)
                timestamp = new Date(log.timestamp * 1000)
                logs_all_html += "#{log.fabscript}: #{log.msg}[#{log.status}] #{timestamp}<br>"

            id_logs = "log_#{i}"
            result_cluster_map[cluster] = cluster_data
            logs_html = """
<a class="popover-anchor" data-containe="body" data-toggle="popover" data-placement="bottom" data-html="true" data-content="#{logs_all_html}">
    #{tmp_logs_html}
 </a>
            """

            if hash == '#all' or hash == "##{cluster}"
                results_tbody.append("
                <tr id=\"#{result.pk}\">
                    <td><input type=\"checkbox\"></td>
                    <td>#{result.fields.node_path}</td>
                    <td>#{result.fields.status}</td>
                    <td>#{result.fields.msg}</td>
                    <td>#{logs_html}</td>
                    <td>#{result.fields.updated_at}</td>
                </tr>")

        clusters_html = ''
        for cluster, results of result_cluster_map
            active = ""
            if hash == "##{cluster}"
                active = "active"
            clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{results.length})</a></li>"

        $('#result-clusters').html(clusters_html)

        graph_nodes = []
        graph_links = []
        for fabscript, fabscript_node of fabscript_node_map
            graph_nodes[fabscript_node.index] = {
                name: fabscript,
                success_length: fabscript_node.success_nodes.length,
                failed_length: fabscript_node.failed_nodes.length,
            }

            for link in fabscript_node.links
                graph_links.push({
                    'source': fabscript_node.index,
                    'target': link,
                })

        console.log graph_nodes
        console.log graph_links
