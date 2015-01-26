render_node_clusters = ->
    console.log node_clusters
    paths = location.pathname.split('/', 3)
    page = paths[1]
    cluster_pk = parseInt(paths[2])

    if cluster_pk == 0
        active = 'active'
    else
        active = ''

    clusters_html = $("""<div class="panel-group" id="accordion">
                <div class="panel">
                    <div class="panel-heading">
                        <span>
                            <span class="panel-title">root</span>
                            <a class="pjax pull-right show #{active}"
                                    href="/#{page}/0/">show</a>
                        </span>
                    </div>
                </div>
            </div>""")

    expand_clusters = (html, clusters) ->
        console.log html
        parent_id = html.prop('id')
        console.log parent_id
        console.log clusters

        for node_cluster in clusters
            tmp_clusters = []
            full_name = node_cluster.fields.name
            if not node_cluster.name?
                node_cluster.name = full_name

            splited_cluster = node_cluster.name.split('/')

            if splited_cluster.length > 1
                tmp_name = splited_cluster.slice(1).join('/')
                tmp_cluster = node_cluster
                tmp_cluster.name = tmp_name
                tmp_clusters.push(tmp_cluster)

            name = splited_cluster[0]
            collapse_id = "#{parent_id}-#{name}"
            collapse_panel_id = "#{parent_id}-panel-#{name}"
            collapse_head_id = "#{parent_id}-head-#{name}"
            collapse_body_id = "#{parent_id}-body-#{name}"
            collapse_body = html.find("##{collapse_body_id}")
            if collapse_body.length == 0
                active = ''
                if splited_cluster.length == 1
                    if cluster_pk == node_cluster.pk
                        active = 'active'
                        # TODO jsonオブジェクトをいいかんじに表示する
                        # data = JSON.parse(node_cluster.fields.data)
                        $('#cluster-data').html(node_cluster.fields.data)

                    show = """<a class="pjax pull-right show #{active}" href="/#{page}/#{node_cluster.pk}/">show</a>"""

                else
                    show = ""

                html.append("""
                <div class="panel" id="#{collapse_panel_id}">
                    <div class="panel-heading" id="#{collapse_head_id}">
                        <span>
                            <a class="panel-title collapsed" data-toggle="collapse"
                                    data-parent="##{parent_id}" href="##{collapse_id}"
                                    aria-controls="#{collapse_id}">#{name}</a>
                            #{show}
                        </span>
                    </div>
                    <div id="#{collapse_id}" class="panel-collapse collapse"
                            aria-labelledby="#{collapse_head_id}">
                        <div class="panel-body panel-group" id="#{collapse_body_id}">
                        </div>
                    </div>
                </div>
                """)

                collapse_body = html.find("##{collapse_body_id}")

                if cluster_pk == node_cluster.pk and splited_cluster.length == 1
                    html.find("##{collapse_id}").parents('.collapse').addClass('in')
                    html.find("##{collapse_panel_id}").parents('.panel').find('> .panel-heading .panel-title').removeClass('collapsed')

            expand_clusters(collapse_body, tmp_clusters)

    expand_clusters(clusters_html, node_clusters)

    $('#sidebar').html(clusters_html)


render_fabscript_clusters = ->
    paths = location.pathname.split('/', 3)
    page = paths[1]
    cluster_hash = location.hash

    clusters_html = $("""
        <div class="panel-group" id="accordion">
            <div class="panel">
                <div class="panel-heading">
                    <span>
                        <span class="panel-title">root</span>
                        <a class="pjax pull-right show"
                                href="#root">show</a>
                    </span>
                </div>
            </div>
        </div>""")

    expand_clusters = (html, clusters, parent, is_init) ->
        clusters = clusters
        parent_id = html.attr('id')

        for node_cluster in clusters
            tmp_clusters = []
            full_name = node_cluster.fields.name
            if is_init
                node_cluster.name = full_name

            splited_cluster = node_cluster.name.split('.')

            if splited_cluster.length > 1
                tmp_name = splited_cluster.slice(1).join('.')
                tmp_cluster = node_cluster
                tmp_cluster.name = tmp_name
                tmp_clusters.push(tmp_cluster)

            name = splited_cluster[0]
            if parent == null
                parent_name = name
            else
                parent_name = "#{parent}.#{name}"

            collapse_id = "#{parent_id}-#{name}"
            collapse_panel_id = "#{parent_id}-panel-#{name}"
            collapse_head_id = "#{parent_id}-head-#{name}"
            collapse_body_id = "#{parent_id}-body-#{name}"
            collapse_body = html.find("##{collapse_body_id}")
            if collapse_body.length == 0
                if cluster_hash == "##{parent_name}"
                    active = 'active'
                else
                    active = ''

                show = """<a class="pjax pull-right show #{active}" href="##{parent_name}">show</a>"""

                html.append("""
                <div class="panel" id="#{collapse_panel_id}">
                    <div class="panel-heading" id="#{collapse_head_id}">
                        <span>
                            <a class="panel-title collapsed" data-toggle="collapse"
                                    data-parent="##{parent_id}" href="##{collapse_id}"
                                    aria-controls="#{collapse_id}">#{name}</a>
                            #{show}
                        </span>
                    </div>
                    <div id="#{collapse_id}" class="panel-collapse collapse"
                            aria-labelledby="#{collapse_head_id}">
                        <div class="panel-body panel-group" id="#{collapse_body_id}">
                        </div>
                    </div>
                </div>
                """)

                collapse_body = html.find("##{collapse_body_id}")

                if cluster_hash == "##{parent_name}"
                    html.find("##{collapse_id}").parents('.collapse').addClass('in')
                    html.find("##{collapse_panel_id}").parents('.panel')
                        .find('> .panel-heading .panel-title').removeClass('collapsed')

            expand_clusters(collapse_body, tmp_clusters, parent_name, false)

    expand_clusters(clusters_html, fabscripts, null, true)

    $('#sidebar').html(clusters_html)
