render_all = ->
    if mode.current == mode.USER
        render_user()
    else if mode.current == mode.NODE
        render_node_clusters()
        render_node_cluster()
        $('.tablesorter').tablesorter({
            sortList: [[0, -1], [1, 0]]
        })

    $('[data-toggle=popover]').popover()


init = ->
    $('#show-graph').on('click', ->
        $('#graph-modal').modal()
        return)

    $('#graph-modal').on('shown.bs.modal', ->
        render_force_layout()
        return)

    $('#show-overview').on('click', ->
        $('#overview-modal').modal()
        return)

    $('#overview-modal').on('shown.bs.modal', ->
        render_overview_layout()
        return)

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
    if node_cluster.length > 0
        mode.current = mode.NODE
        node_cluster = JSON.parse(node_cluster.html())

    render_all()

    return

init()

if $.support.pjax
    $(document).pjax('.pjax', '#pjax-container')
    $(document).on('pjax:end', ->
        pathname = location.pathname.split('/', 2)
        $('.pjax').parent().removeClass('active')
        if pathname[1] == ''
            $('a[href="/"]').parent().addClass('active')
        else
            $('a[href="/' + pathname[1] + '/"]').parent().addClass('active')
        init()
        return)

$(window).on('hashchange', ->
    if location.hash != ''
        render_all()

    return)
