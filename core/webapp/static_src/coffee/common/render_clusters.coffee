render_node_clusters = ->
    console.log('test')
    console.log node_clusters
    paths = location.pathname.split('/', 3)
    page = paths[1]
    cluster_pk = parseInt(paths[2])

    if cluster_pk == 0
        active = 'active'
    else
        active = ''

    clusters_html = """
        <li class="#{active}"><a class="pjax" href="/#{page}/0/">root</a></li>"""
    for node_cluster in node_clusters
        active = ''
        if node_cluster.pk == cluster_pk
            active = "active"

        clusters_html += "<li class=\"#{active}\">
            <a class=\"pjax\" href=\"/#{page}/#{node_cluster.pk}/\">
            #{node_cluster.fields.name}</a>
            </li>"

    $('#node-clusters-ul').html(clusters_html)
