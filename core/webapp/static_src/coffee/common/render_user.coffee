render_user = ->
    users_tbody = $('#users-tbody')
    if users_tbody.length > 0
        hash = location.hash
        if hash == ''
            hash = '#user-list'

        $('.user-content').hide()
        if hash == '#user-list'
            users_tbody.empty()
            console.log users
            for user in users
                users_tbody.append("
                <tr id=\"#{user.pk}\">
                    <td><input type=\"checkbox\"></td>
                    <td>#{user.fields.username}</td>
                    <td>#{user.fields.is_superuser}</td>
                </tr>")
            $('#user-list').show()
        else if hash == '#change-password'
            $('#change-password').show()
        else if hash == '#create-user'
            $('#create-user').show()

        $("#left-nav > li").removeClass('active')
        $("#{hash}-li").addClass('active')
