render_node = ->
    nodes_tbody_html = ''
    for node in nodes
        nodes_tbody_html += "
        <tr id=\"#{node.pk}\">
            <td><input type=\"checkbox\"></td>
            <td>#{node.fields.path}</td>
            <td>#{node.fields.host}</td>
            <td>#{node.fields.ip}</td>
            <td>#{node.fields.uptime}</td>
            <td>#{node.fields.ssh}</td>
        </tr>"

    $('#nodes-tbody').empty().html(nodes_tbody_html)

    render_node_clusters()
