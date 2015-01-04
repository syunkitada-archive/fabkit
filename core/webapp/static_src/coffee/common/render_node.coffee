render_node = ->
    nodes_tbody_html = ''
    for node in nodes
        data = JSON.parse(node.fields.data)
        console.log data
        if Object.keys(data).length == 0
            data_html = "No data"
        else
            data_html = "<table class='table table-bordered'><tbody>"
            for key, value of data
                # TODO valueがObjectだったら再帰的に展開
                data_html += """
                    <tr>
                        <td>#{key}</td>
                        <td>#{value}</td>
                    </tr>"""

            data_html += '</tbody></table>'

        host_html = """
            <a class="popover-anchor" data-containe="body" data-toggle="popover"
                data-placement="bottom" data-html="true" data-title="Data" data-content="#{data_html}">
                #{node.fields.host}
            </a>"""

        nodes_tbody_html += "
        <tr id=\"#{node.pk}\">
            <td><input type=\"checkbox\"></td>
            <td>#{node.fields.path}</td>
            <td>#{host_html}</td>
            <td>#{node.fields.ip}</td>
            <td>#{node.fields.uptime}</td>
            <td>#{node.fields.ssh}</td>
        </tr>"

    $('#nodes-tbody').empty().html(nodes_tbody_html)

    render_node_clusters()
