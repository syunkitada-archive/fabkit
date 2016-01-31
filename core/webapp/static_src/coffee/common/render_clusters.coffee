render_node_clusters = (clusters)->
    if mode.current == mode.NODE
        paths = location.pathname.split('node/')
        page = 'node'
        cluster_path = paths[1].slice(0, -1)
        if cluster_path == ''
            cluster_path = 'recent'

    else if mode.current == mode.CHAT
        paths = location.pathname.split('chat/')
        page = 'chat'
        cluster_path = paths[1].slice(0, -1)
        if cluster_path == ''
            cluster_path = 'all'

    clusters_html = $("""<div class="panel-group" id="accordion">
            </div>""")

    expand_clusters = (html, clusters, root_cluster) ->
        if not clusters?
            return

        parent_id = html.prop('id')

        for cluster_name in clusters
            splited_cluster = cluster_name.split('/')

            # 子のクラスタ階層が続くならtmp_clusterに入れておく
            tmp_clusters = []
            if splited_cluster.length > 1
                tmp_name = splited_cluster.slice(1).join('/')
                tmp_clusters.push(tmp_name)

            # 現在のクラスタ階層のhtmlを作成
            name = splited_cluster[0]
            if root_cluster == null
                tmp_root_cluster = name
            else
                tmp_root_cluster = root_cluster + '/' + name
            collapse_id = "#{parent_id}-#{name}"
            collapse_panel_id = "#{parent_id}-panel-#{name}"
            collapse_head_id = "#{parent_id}-head-#{name}"
            collapse_body_id = "#{parent_id}-body-#{name}"
            collapse_body = html.find("##{collapse_body_id}")
            if collapse_body.length == 0
                active = ''
                if splited_cluster.length == 1
                    tmp_root_cluster = tmp_root_cluster.replace(/__/g, '/')
                    if tmp_root_cluster == cluster_path
                        active = 'active'

                    show = """<a class="pjax pull-right show #{active}" href="/#{page}/#{tmp_root_cluster}/">show</a>"""

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

                if tmp_root_cluster == cluster_path and splited_cluster.length == 1
                    html.find("##{collapse_id}").parents('.collapse').addClass('in')
                    html.find("##{collapse_panel_id}").parents('.panel').find('> .panel-heading .panel-title').removeClass('collapsed')

            if tmp_clusters.length > 0
                expand_clusters(collapse_body, tmp_clusters, tmp_root_cluster)

    expand_clusters(clusters_html, clusters, null)

    $('#sidebar').html(clusters_html)
