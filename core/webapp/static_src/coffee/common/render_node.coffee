render_node = ->
    nodes = $('#nodes')
    nodes_tbody = $('#nodes-tbody')
    if nodes_tbody.length > 0
        nodes = JSON.parse(nodes.html())
        node_cluster_map = {'all': nodes}
        hash = location.hash
        if hash == ''
            hash = '#all'

        nodes_tbody.empty()
        for node in nodes
            cluster = node.fields.path.split('/')[0]
            if cluster of node_cluster_map
                cluster_data = node_cluster_map[cluster]
                cluster_data.push(node)
            else
                cluster_data = [node]

            node_cluster_map[cluster] = cluster_data

            if hash == '#all' or hash == "##{cluster}"
                nodes_tbody.append("
                <tr>
                    <td>#{node.fields.path}</td>
                    <td>#{node.fields.host}</td>
                    <td>#{node.fields.ip}</td>
                    <td>#{node.fields.uptime}</td>
                    <td>#{node.fields.ssh}</td>
                </tr>")


        clusters_html = ''
        for cluster, nodes of node_cluster_map
            active = ""
            if hash == "##{cluster}"
                active = "active"
            clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{nodes.length})</a></li>"

        $('#node-clusters').html(clusters_html)
