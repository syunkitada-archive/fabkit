render_tasks = ->
    fabscript_node_map = {}
    fabscripts = []

    all_node_length = 0
    processing_node_length = 0
    success_node_length = 0
    warning_node_length = 0
    danger_node_length = 0

    tasks_tbody_html = ''
    jobs_tbody_html = ''

    job_map = {}

    for task in tasks
        all_node_length++
        is_warning = false
        is_danger = false
        is_processing = false
        status_html = task.status
        if task.status == 'error'
            is_danger = true
        else if task.status == 'processing'
            is_processing = true
            status_html = """<div class="progress" style="margin: 0px;">
              <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">
                #{task.status}
              </div>
            </div>"""

        if is_danger
            node_class = 'danger'
            danger_node_length++
        else if is_warning
            node_class = 'warning'
            warning_node_length++
        else if is_processing
            processing_node_length++
        else
            node_class = ''
            success_node_length++

        tasks_tbody_html += """
            <tr class="#{node_class}">
                <td>#{task.method}</td>
                <td>#{task.target}</td>
                <td>#{task.owner}</td>
                <td>#{status_html}</td>
                <td>#{task.json_arg}</td>
                <td>#{task.msg}</td>
                <td>#{task.updated_at}</td>
                <td>#{task.created_at}</td>
            </tr>"""

        if task.target not of job_map
            job_map[task.target] = task
            arg = JSON.parse(task.json_arg)
            jobs_tbody_html += """
            <tr class="#{node_class}">
                <td>#{task.target}</td>
                <td>#{task.owner}</td>
                <td>#{status_html}</td>
                <td>#{task.json_arg}</td>
                <td>#{task.msg}</td>
                <td>#{task.updated_at}</td>
                <td>#{task.created_at}</td>
            </tr>"""

    console.log 'DEBUG'
    console.log job_map

    $('#all-node-badge').html(all_node_length)
    $('#success-node-badge').html(success_node_length)
    $('#processing-node-badge').html(processing_node_length)
    $('#warning-node-badge').html(warning_node_length)
    $('#danger-node-badge').html(danger_node_length)
    $('#tasks-tbody').html(tasks_tbody_html)
    $('#jobs-tbody').html(jobs_tbody_html)

    refresh = () ->
        $.ajax({
            url: location.path_name,
            data: {'query': 'get_tasks'}
            success: (data) ->
                tasks = data.tasks
                render_tasks()
        })

    setTimeout(refresh, 30000)
