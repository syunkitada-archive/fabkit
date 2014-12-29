filter = ->
    query = $(this).val()
    trs = $('tbody > tr')
    for tr in trs
        tr = $(tr)
        tds = tr.find('td')
        is_match = false
        for td in tds
            if td.innerHTML.match(query)
                is_match = true
                break
        if is_match
            tr.show()
        else
            tr.hide()

    return


fabkit.remove_data = (url) ->
    target_html = ''
    trs = $('tbody > tr')
    for tr in trs
        tr = $(tr)
        if tr.is(':visible')
            if tr.find('input[type=checkbox]').prop('checked')
                target_html += """
                <li>
                    #{tr.find('td')[1].innerHTML}
                </li>
                <input type="hidden" name="target" value="#{tr.prop('id')}">
                """
                continue

    if target_html == ''
        target_html = '<li>Not selected</li>'
        $('#remove-submit').attr('disabled', true)
    else
        $('#remove-submit').attr('disabled', false)

    $('#remove-form').prop('action', url)
    $('#modal-progress').hide()
    $('#modal-msg').hide()
    $('#target-list').html(target_html)
    $('#remove-modal').modal()
    return


$('#remove-form').on('submit', ->
    event.preventDefault(false)
    form = $(this)
    submit_button = form.find('[type=submit]')
    data = form.serialize()
    $.ajax
        url: form.attr('action'),
        type: form.attr('method'),
        data: form.serialize(),
        beforeSend: (xhr, settings) ->
            $('#modal-progress').show()
            submit_button.attr('disabled', true)
            return
        complete: (xhr, textStatus) ->
            $('#modal-progress').hide()
            return
        success: (data) ->
            console.log data
            $('#modal-msg').html('<div class="bg-success msg-box">Success</div>').show()
            target_list = $('#target-list')
            targets = $('input[name=target]')
            tmp_targets = []
            for target in targets
                tmp_targets.push(parseInt($(target).val()))

            if $('#nodes-tbody').length > 0
                tmp_nodes = []
                for node in nodes
                    pk = node.pk
                    if node.pk not in tmp_targets
                        tmp_nodes.push(node)

                nodes = tmp_nodes

            else if $('#fabscripts-tbody').length > 0
                tmp_fabscripts = []
                console.log tmp_targets
                console.log fabscripts
                for fabscript in fabscripts
                    pk = fabscript.pk
                    if fabscript.pk not in tmp_targets
                        tmp_fabscripts.push(fabscript)

                fabscripts = tmp_fabscripts
                console.log fabscripts

            else if $('#results-tbody').length > 0
                tmp_results = []
                for result in results
                    pk = result.pk
                    if result.pk not in tmp_targets
                        tmp_results.push(result)

                results = tmp_results

            else if $('#users-tbody').length > 0
                tmp_users = []
                for user in users
                    pk = user.pk
                    if user.pk not in tmp_targets
                        tmp_users.push(user)

                users = tmp_users

            console.log 'DEBUG'
            render_all()
            return
        error: (xhr, textStatus, error) ->
            $('#modal-msg').html('<div class="bg-danger msg-box">Failed</div>').show()
            console.log textStatus
            return

    return)
