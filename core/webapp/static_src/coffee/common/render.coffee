render_all = ->
    render_user()
    render_fabscript()
    render_node()
    render_result()


init = ->
    $('[data-toggle=popover]').popover()

    $('#show-graph').on('click', ->
        $('#graph-modal').modal()
        return)

    $('#graph-modal').on('shown.bs.modal', ->
        render_force_layout()
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
        users = JSON.parse(users.html())

    nodes = $('#nodes')
    if nodes.length > 0
        nodes = JSON.parse(nodes.html())
        console.log nodes

    fabscripts = $('#fabscripts')
    if fabscripts.length > 0
        console.log 'test'
        fabscripts = JSON.parse(fabscripts.html())
        for fabscript in fabscripts
            fabscript.fields.link = JSON.parse(fabscript.fields.link)
            fabscript.fields.linked_fabscripts = JSON.parse(fabscript.fields.linked_fabscripts)

    results = $('#results')
    if results.length > 0
        results = JSON.parse(results.html())

    render_all()

    return


if $.support.pjax
    $(document).pjax('.pjax', '#pjax-container')
    $(document).on('pjax:end', ->
        $('.pjax').parent().removeClass('active')
        $('a[href="' + location.pathname + '"]').parent().addClass('active')
        init()
        return)


$(window).on('hashchange', ->
    init()
    return)


init()
