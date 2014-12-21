console.log 'test'

if $.support.pjax
    $(document).pjax('.pjax', '#pjax-container')
    $(document).on('pjax:end', ->
        $('.pjax').parent().removeClass('active')
        $('a[href="' + location.pathname + '"]').parent().addClass('active')
        render_fabscripts()
        render_nodes()
        render_results()
    )


render_fabscripts = ->
    fabscripts = $('#fabscripts')
    fabscripts_tbody = $('#fabscripts-tbody')
    if fabscripts_tbody.length > 0
        scripts = JSON.parse(fabscripts.html())
        fabscript_cluster_map = {'all': scripts}
        hash = location.hash
        if hash == ''
            hash = '#all'

        fabscripts_tbody.empty()
        for script in scripts
            script.fields.connection = JSON.parse(script.fields.connection)
            script.fields.connected_fabscripts = JSON.parse(script.fields.connected_fabscripts)

            connected_html = '<ul>'
            for connected in script.fields.connected_fabscripts
                connected_html += "<li>#{connected}</li>"
            connected_html += '</ul>'

            cluster = script.fields.name.split('.')[0]
            if cluster of fabscript_cluster_map
                cluster_data = fabscript_cluster_map[cluster]
                cluster_data.push(script)
            else
                cluster_data = [script]

            fabscript_cluster_map[cluster] = cluster_data

            if hash == '#all' or hash == "##{cluster}"
                fabscripts_tbody.append("
                <tr>
                    <td>#{script.fields.name}</td>
                    <td>#{connected_html}</td>
                    <td>#{script.fields.updated_at}</td>
                </tr>")


        clusters_html = ''
        for cluster, scripts of fabscript_cluster_map
            active = ""
            if hash == "##{cluster}"
                active = "active"
            clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{scripts.length})</a></li>"

        console.log clusters_html
        $('#fabscript-clusters').html(clusters_html)

render_nodes = ->
    nodes = $('#nodes')
    nodes_tbody = $('#nodes-tbody')
    if nodes_tbody.length > 0
        nodes = JSON.parse(nodes.html())
        console.log(nodes)
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

        console.log clusters_html
        $('#node-clusters').html(clusters_html)


render_results = ->
    results = $('#results')
    nodes = $('#nodes')
    results_tbody = $('#results-tbody')
    console.log results
    if results_tbody.length > 0
        results = JSON.parse(results.html())
        console.log results
        result_cluster_map = {'all': results}
        hash = location.hash
        if hash == ''
            hash = '#all'

        results_tbody.empty()
        for result in results
            cluster = result.fields.node_path.split('/')[0]
            if cluster of result_cluster_map
                cluster_data = result_cluster_map[cluster]
                cluster_data.push(result)
            else
                cluster_data = [result]

            result_cluster_map[cluster] = cluster_data

            if hash == '#all' or hash == "##{cluster}"
                results_tbody.append("
                <tr>
                    <td>#{result.fields.node_path}</td>
                    <td>#{result.fields.status}</td>
                    <td>#{result.fields.msg}</td>
                    <td>#{result.fields.logs}</td>
                    <td>#{result.fields.logs_all}</td>
                    <td>#{result.fields.updated_at}</td>
                </tr>")


        clusters_html = ''
        for cluster, results of result_cluster_map
            active = ""
            if hash == "##{cluster}"
                active = "active"
            clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{results.length})</a></li>"

        console.log clusters_html
        $('#result-clusters').html(clusters_html)

render_fabscripts()
render_nodes()
render_results()

$(window).on('hashchange', ->
    render_fabscripts()
    render_nodes()
    render_results()
    return)
