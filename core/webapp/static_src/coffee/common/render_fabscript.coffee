render_fabscript = ->
    fabscripts_tbody = $('#fabscripts-tbody')
    if fabscripts_tbody.length > 0
        node_map = {}
        nodes = []
        links = []

        fabscript_cluster_map = {'all': fabscripts}
        hash = location.hash
        if hash == ''
            hash = '#all'

        fabscripts_tbody.empty()
        for script in fabscripts
            connected_html = ''
            for connected in script.fields.connected_fabscripts
                connected_html += "#{connected}</br>"

            cluster = script.fields.name.split('.')[0]
            if cluster of fabscript_cluster_map
                cluster_data = fabscript_cluster_map[cluster]
                cluster_data.push(script)
            else
                cluster_data = [script]

            fabscript_cluster_map[cluster] = cluster_data

            if hash == '#all' or hash == "##{cluster}"
                fabscripts_tbody.append("
                <tr id=\"#{script.pk}\">
                    <td><input type=\"checkbox\"></td>
                    <td>#{script.fields.name}</td>
                    <td>#{connected_html}</td>
                    <td>#{script.fields.updated_at}</td>
                </tr>")

                if hash != "#all"
                    is_exist = false
                    node_index = 0
                    for node, i in nodes
                        if node.name == script.fields.name
                            is_exist = true
                            node_index = i
                            break
                    if not is_exist
                        node_index = nodes.length
                        nodes.push(
                            'name': script.fields.name,
                        )

                    for fabscript in script.fields.connected_fabscripts
                        fabscript = fabscript.split(':')[0]
                        is_exist = false
                        linked_index = 0
                        for node, i in nodes
                            if node.name == fabscript
                                is_exist = true
                                linked_index = i
                                break

                        if not is_exist
                            linked_index = nodes.length
                            nodes.push({
                                'name': fabscript,
                            })

                        if node_index != linked_index
                            links.push({
                                'source': linked_index,
                                'target': node_index,
                            })

        clusters_html = ''
        for cluster, fabscripts of fabscript_cluster_map
            active = ""
            if hash == "##{cluster}"
                active = "active"
            clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{fabscripts.length})</a></li>"

        $('#fabscript-clusters').html(clusters_html)

        $('#svg-fabscript').empty()
        if hash != "#all"
            render_force_layout('#svg-fabscript', nodes, links)
