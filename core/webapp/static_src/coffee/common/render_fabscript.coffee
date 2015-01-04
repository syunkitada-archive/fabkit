render_fabscript = ->
    hash = location.hash
    if hash == ''
        hash = '#all'

    graph_nodes = []
    graph_links = []

    fabscript_cluster_map = {'all': fabscripts}

    fabscripts_tbody = ''
    for script in fabscripts
        linked_html = ''
        for linked in script.fields.linked_fabscripts
            linked_html += "#{linked}</br>"

        cluster = script.fields.name.split('.')[0]
        if cluster of fabscript_cluster_map
            cluster_data = fabscript_cluster_map[cluster]
            cluster_data.push(script)
        else
            cluster_data = [script]

        fabscript_cluster_map[cluster] = cluster_data

        if hash == '#all' or hash == "##{cluster}"
            fabscripts_tbody += "
            <tr id=\"#{script.pk}\">
                <td><input type=\"checkbox\"></td>
                <td>#{script.fields.name}</td>
                <td>#{linked_html}</td>
                <td>#{script.fields.updated_at}</td>
            </tr>"

            if hash != "#all"
                is_exist = false
                node_index = 0
                for node, i in graph_nodes
                    if node.name == script.fields.name
                        is_exist = true
                        node_index = i
                        break
                if not is_exist
                    node_index = graph_nodes.length
                    graph_nodes.push(
                        'name': script.fields.name,
                    )

                for fabscript in script.fields.linked_fabscripts
                    fabscript = fabscript.split(':')[0]
                    is_exist = false
                    linked_index = 0
                    for node, i in graph_nodes
                        if node.name == fabscript
                            is_exist = true
                            linked_index = i
                            break

                    if not is_exist
                        linked_index = graph_nodes.length
                        graph_nodes.push({
                            'name': fabscript,
                        })

                    if node_index != linked_index
                        graph_links.push({
                            'source': linked_index,
                            'target': node_index,
                        })


    $('#fabscripts-tbody').html(fabscripts_tbody)

    clusters_html = ''
    for cluster, scripts of fabscript_cluster_map
        active = ""
        if hash == "##{cluster}"
            active = "active"
        clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{scripts.length})</a></li>"

    $('#fabscript-clusters').html(clusters_html)

    if hash == '#all'
        $('#show-graph').hide()
    else
        $('#show-graph').show()
