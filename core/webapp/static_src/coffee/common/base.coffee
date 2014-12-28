bind_popover = ->
    $('[data-toggle=popover]').popover()

render_fabscript()
render_node()
render_result()
bind_popover()


if $.support.pjax
    $(document).pjax('.pjax', '#pjax-container')
    $(document).on('pjax:end', ->
        $('.pjax').parent().removeClass('active')
        $('a[href="' + location.pathname + '"]').parent().addClass('active')
        render_fabscript()
        render_node()
        render_result()
        return)


$(window).on('hashchange', ->
    render_fabscript()
    render_node()
    render_result()
    return)
