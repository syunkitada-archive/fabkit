update_pagedata = ->
    if mode.current == mode.NODE
        paths = location.pathname.split('node/')
        current_page = 'node'
        current_cluster_path = paths[1].slice(0, -1)
        if current_cluster_path == ''
            current_cluster_path = 'recent'

    else if mode.current == mode.AGENT
        paths = location.pathname.split('agent/')
        current_page = 'agent'
        current_cluster_path = paths[1].slice(0, -1)
        if current_cluster_path == ''
            current_cluster_path = current_cluster

    else if mode.current == mode.TASK
        paths = location.pathname.split('task/')
        current_page = 'task'
        current_cluster_path = paths[1].slice(0, -1)
        if current_cluster_path == ''
            current_cluster_path = current_cluster

    else if mode.current == mode.CHAT
        paths = location.pathname.split('chat/')
        current_page = 'chat'
        current_cluster_path = paths[1].slice(0, -1)
        if current_cluster_path == ''
            current_cluster_path = 'all'

render_all = ->
    if mode.current == mode.USER
        render_user()
    else if mode.current == mode.NODE
        render_node_clusters(node_clusters)
        render_node_cluster()

        if $('#nodes-tbody > tr').length != 0
            $('#node-table').tablesorter({
                sortList: [[0, 1], [1, 0]]
            })

        render_datamap()
        bind_shown_tab_event()

        tab = 0
        $('#datamap-modal').on('shown.bs.modal', ->
            console.log 'shown'
            $("#map-#{datamap_tabs[tab]}").tab('show')
            return)

        $('#show-datamap').on('click', ->
            $('#datamap-modal').modal()
            tab = 0
            if datamap_tabs.length > 2
                tab = 2
            return)

        $('#show-statusmap').on('click', ->
            tab = 0
            $('#datamap-modal').modal()
            return)

        $('#show-relationmap').on('click', ->
            tab = 1
            $('#datamap-modal').modal()
            return)

    else if mode.current == mode.AGENT
        render_node_clusters(agent_clusters)
        render_node_cluster()

        $('#node-table').tablesorter({
            sortList: [[0, 1], [1, 0]]
        })

        render_datamap()
        bind_shown_tab_event()

        tab = 0
        $('#datamap-modal').on('shown.bs.modal', ->
            console.log 'shown'
            $("#map-#{datamap_tabs[tab]}").tab('show')
            return)

        $('#show-datamap').on('click', ->
            $('#datamap-modal').modal()
            tab = 0
            if datamap_tabs.length > 2
                tab = 2
            return)

        $('#show-statusmap').on('click', ->
            tab = 0
            $('#datamap-modal').modal()
            return)

        $('#show-relationmap').on('click', ->
            tab = 1
            $('#datamap-modal').modal()
            return)

    else if mode.current == mode.TASK
        render_node_clusters(agent_clusters)

        $('#task-table').tablesorter()

    $('[data-toggle=popover]').popover()

apps.init = ->
    apps.log 'called init'

    $('#search-input').on('change', filter)
                      .on('keyup', filter)

    $('#all-checkbox').on('change', ->
        is_checked = $(this).prop('checked')
        trs = $('tbody > tr')
        for tr in trs
            tr = $(tr)
            if tr.is(':visible')
                tr.find('input[type=checkbox]').prop('checked', is_checked)
            else
                tr.find('input[type=checkbox]').prop('checked', false)
        return)

    users = $('#users')
    if users.length > 0
        mode.current = mode.USER
        users = JSON.parse(users.html())

    node_clusters = $('#node_clusters')
    if node_clusters.length > 0
        node_clusters = JSON.parse(node_clusters.html())

    node_cluster = $('#node_cluster')
    if location.pathname.indexOf('/node/') == 0
        mode.current = mode.NODE
        node_cluster = JSON.parse(node_cluster.html())

    else if location.pathname.indexOf('/agent/') == 0
        mode.current = mode.AGENT
        agent_clusters = JSON.parse($('#agent_clusters').html())
        node_cluster = JSON.parse(node_cluster.html())

    else if location.pathname.indexOf('/task/') == 0
        mode.current = mode.TASK
        agent_clusters = JSON.parse($('#agent_clusters').html())

    else if location.pathname.indexOf('/event/') == 0
        mode.current = mode.EVENT
        agent_clusters = JSON.parse($('#agent_clusters').html())
        node_cluster = JSON.parse(node_cluster.html())

    else if location.pathname.indexOf('/chat/') == 0
        mode.current = mode.CHAT
        # render_node_clusters(room_clusters)

    render_all()

    apps.init_chat()

    return

if $.support.pjax
    $(document).pjax('.pjax', '#pjax-container')
    $(document).on('pjax:end', ->
        pathname = location.pathname.split('/', 2)
        $('.pjax').parent().removeClass('active')
        if pathname[1] == ''
            $('a[href="/"]').parent().addClass('active')
        else
            $('a[href="/' + pathname[1] + '/"]').parent().addClass('active')
        apps.init()
        change_chat_cluster()
        return)

$(window).on('hashchange', ->
    if location.hash != ''
        render_all()

    return)
