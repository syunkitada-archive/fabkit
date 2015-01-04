render_fabscript = ->
    hash = location.hash
    if hash == ''
        hash = '#all'

    if hash == '#all'
        $('#show-graph').hide()
    else
        $('#show-graph').show()

    graph_nodes = []
    graph_links = []

    fabscript_cluster_map = {'all': fabscripts}

    fabscripts_tbody = ''
    for fabscript in fabscripts
        linked_html = ''
        for linked in fabscript.fields.linked_fabscripts
            linked_html += "#{linked}</br>"

        cluster = fabscript.fields.name.split('.')[0]
        if cluster of fabscript_cluster_map
            cluster_data = fabscript_cluster_map[cluster]
            cluster_data.push(fabscript)
        else
            cluster_data = [fabscript]

        fabscript_cluster_map[cluster] = cluster_data

        if hash == '#all' or hash == "##{cluster}"
            fabscripts_tbody += "
            <tr id=\"#{fabscript.pk}\">
                <td><input type=\"checkbox\"></td>
                <td>#{fabscript.fields.name}</td>
                <td>#{linked_html}</td>
                <td>#{fabscript.fields.updated_at}</td>
            </tr>"

            if hash != "#all"
                is_exist = false
                node_index = 0
                for node, i in graph_nodes
                    if node.name == fabscript.fields.name
                        is_exist = true
                        node_index = i
                        break

                if not is_exist
                    node_index = graph_nodes.length
                    graph_nodes.push(
                        'name': fabscript.fields.name,
                    )

                for linked in fabscript.fields.linked_fabscripts
                    linked = linked.split(':')[0]
                    is_exist = false
                    linked_index = 0
                    for node, i in graph_nodes
                        if node.name == linked
                            is_exist = true
                            linked_index = i
                            break

                    if not is_exist
                        linked_index = graph_nodes.length
                        graph_nodes.push({
                            'name': linked,
                        })

                    if node_index != linked_index
                        graph_links.push({
                            'source': linked_index,
                            'target': node_index,
                        })


    $('#fabscripts-tbody').html(fabscripts_tbody)

    fabscript_clusters_ul = ''
    for cluster, scripts of fabscript_cluster_map
        active = ""
        if hash == "##{cluster}"
            active = "active"

        fabscript_clusters_ul += """
            <li class="#{active}">
                <a href="##{cluster}">
                #{cluster} (#{scripts.length})
                </a>
            </li>"""

    $('#fabscript-clusters-ul').html(fabscript_clusters_ul)
