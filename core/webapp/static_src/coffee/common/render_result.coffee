render_result = ->
    results = $('#results')
    nodes = $('#nodes')
    results_tbody = $('#results-tbody')
    if results_tbody.length > 0
        results = JSON.parse(results.html())
        result_cluster_map = {'all': results}
        hash = location.hash
        if hash == ''
            hash = '#all'

        results_tbody.empty()
        for result, i in results
            cluster = result.fields.node_path.split('/')[0]
            if cluster of result_cluster_map
                cluster_data = result_cluster_map[cluster]
                cluster_data.push(result)
            else
                cluster_data = [result]

            tmp_logs_html = ''
            for log in JSON.parse(result.fields.logs)
                tmp_logs_html += "#{log.fabscript}: #{log.msg}[#{log.status}]<br>"

            logs_all_html = ''
            for log in JSON.parse(result.fields.logs_all)
                timestamp = new Date(log.timestamp * 1000)
                logs_all_html += "#{log.fabscript}: #{log.msg}[#{log.status}] #{timestamp}<br>"

            # TODO Logsの展開機能のビューを整える、日時とかも表示
            id_logs = "log_#{i}"
            result_cluster_map[cluster] = cluster_data
            # logs_html = """
            #     <a class="collapse-logs collapsed" data-toggle="collapse" data-target="##{id_logs}" aria-expanded="true" aria-controls="#{id_logs}">
            #         #{tmp_logs_html}
            #     </a>

            #     <div id="#{id_logs}" class="collapse">
            #     #{logs_all_html}
            #     </div>
            # """
            logs_html = """
<a class="popover-anchor" data-containe="body" data-toggle="popover" data-placement="bottom" data-html="true" data-content="#{logs_all_html}">
    #{tmp_logs_html}
 </a>
            """

            if hash == '#all' or hash == "##{cluster}"
                results_tbody.append("
                <tr>
                    <td>#{result.fields.node_path}</td>
                    <td>#{result.fields.status}</td>
                    <td>#{result.fields.msg}</td>
                    <td>#{logs_html}</td>
                    <td>#{result.fields.updated_at}</td>
                </tr>")


        clusters_html = ''
        for cluster, results of result_cluster_map
            active = ""
            if hash == "##{cluster}"
                active = "active"
            clusters_html += "<li class=\"#{active}\"><a href=\"##{cluster}\">#{cluster} (#{results.length})</a></li>"

        $('#result-clusters').html(clusters_html)
