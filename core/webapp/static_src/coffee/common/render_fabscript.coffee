render_fabscript = ->
    hash = location.hash
    if hash == ''
        hash = '#root'

    if hash == '#root'
        $('#show-graph').hide()
    else
        $('#show-graph').show()

    graph_nodes = []
    graph_links = []

    fabscripts_tbody = ''
    for fabscript in fabscripts
        linked_html = ''
        for linked in fabscript.fields.linked_fabscripts
            linked_html += "#{linked}</br>"

        if hash == '#root' or "##{fabscript.fields.name}".indexOf("#{hash}.") == 0
            fabscripts_tbody += "
            <tr id=\"#{fabscript.pk}\">
                <td><input type=\"checkbox\"></td>
                <td>#{fabscript.fields.name}</td>
                <td>#{linked_html}</td>
                <td>#{fabscript.fields.updated_at}</td>
            </tr>"

            if hash != "#root"
                is_exist = false
                node_index = 0
                for node, i in graph_nodes
                    if node.name == fabscript.fields.name
                        is_exist = true
                        node_index = i

                        if 'icon' of fabscript.fields.data
                            node.icon = fabscript.fields.data.icon
                        else
                            node.icon = 'computer-retro'

                        break

                if not is_exist
                    if 'icon' of fabscript.fields.data
                        icon = fabscript.fields.data.icon
                    else
                        icon = 'computer-retro'

                    node_index = graph_nodes.length
                    graph_nodes.push(
                        'name': fabscript.fields.name,
                        'icon': icon,
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
                            'icon': icon,
                        })

                    if node_index != linked_index
                        graph_links.push({
                            'source': linked_index,
                            'target': node_index,
                        })

    $('#fabscripts-tbody').html(fabscripts_tbody)
