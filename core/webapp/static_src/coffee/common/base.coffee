console.log 'test'

if $.support.pjax
    $(document).pjax('.pjax', '#pjax-container')
    $(document).on('pjax:end', ->
        $('.pjax').parent().removeClass('active')
        $('a[href="' + location.pathname + '"]').parent().addClass('active')
        render_fabscripts()
    )


render_fabscripts = ->
    fabscripts = $('#fabscripts')
    fabscripts_tbody = $('#fabscripts-tbody')
    if fabscripts.length > 0
        scripts = JSON.parse(fabscripts.html())
        fabscript_cluster_map = {}
        for script in scripts
            script.fields.connection = JSON.parse(script.fields.connection)
            script.fields.connected_fabscripts = JSON.parse(script.fields.connected_fabscripts)

            connected_html = '<ul>'
            for connected in script.fields.connected_fabscripts
                connected_html += "<li>#{connected}</li>"
            connected_html += '</ul>'

            fabscripts_tbody.append("
            <tr>
                <td>#{script.fields.name}</td>
                <td>#{connected_html}</td>
                <td>#{script.fields.updated_at}</td>
            </tr>")

            cluster = script.fields.name.split('.')[0]
            if cluster of fabscript_cluster_map
                cluster_data = fabscript_cluster_map[cluster]
                cluster_data.push(script.fields.name)
            else
                cluster_data = [script.fields.name]

            fabscript_cluster_map[cluster] = cluster_data

        console.log fabscript_cluster_map
        clusters_html = ''
        for cluster of fabscript_cluster_map
            clusters_html += "<li><a href=\"#\">#{cluster}</a></li>"

        console.log clusters_html
        $('#fabscript-clusters').html(clusters_html)



render_fabscripts()
