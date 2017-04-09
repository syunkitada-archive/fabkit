render_monitor = (data) ->
    console.log data
    text = """``` bash
#{data.console_log}
```"""
    $('#monitor-console').html(marked(text))

    table_filter = $('#monitor-stats-table-filter').val()
    tables = []
    if table_filter.length != 0
        for filter in table_filter.split(',')
            tables.push(filter)

    graph_filter = $('#monitor-stats-graph-filter').val()
    if graph_filter.length == 0
        graphs = []
    else
        graphs = graph_filter.split(',')


    stats_table_html = ''

    dstat_stats_map = {
        int: [],
        csw: [],
        io_read: [],
        io_writ: [],
        disk_read: [],
        disk_writ: [],
        net_recv: [],
        net_send: [],
    }

    for key, value of data.stats
        stat_html = "<div><h3>#{key}</h3>"
        table_html = '<div class="table-responsive"><table class="table table-striped table-bordered">'
        lines = value.split('\n')
        table_html += "<tr>"

        is_dstat = false
        if key.indexOf('_dstat.csv') > 0
            is_dstat = true

        dstat = {
            int: {},
            csw: {},
            io_read: {},
            io_writ: {},
            disk_read: {},
            disk_writ: {},
            net_recv: {},
            net_send: {},
        }
        for line, line_index in lines
            columns = line.split(',')
            table_html += '<td>' + columns.join('</td><td>') + '</td></tr>'

            if is_dstat and line_index == 0
                for c, i in columns
                    if c.indexOf('net/') > 0
                        dstat.net_recv[c] = {index: i  , name: key + c + '.recv', type: 'scatter', x: [], y: []}
                        dstat.net_send[c] = {index: i+1, name: key + c + '.send', type: 'scatter', x: [], y: []}

                    else if c.indexOf('io/') > 0
                        dstat.io_read[c] = {index: i  , name: key + c + '.read', type: 'scatter', x: [], y: []}
                        dstat.io_writ[c] = {index: i+1, name: key + c + '.writ', type: 'scatter', x: [], y: []}

                    else if c.indexOf('dsk/') > 0
                        dstat.disk_read[c] = {index: i  , name: key + c + '.read', type: 'scatter', x: [], y: []}
                        dstat.disk_writ[c] = {index: i+1, name: key + c + '.writ', type: 'scatter', x: [], y: []}

            if is_dstat and line_index == 1
                for c, i in columns
                    if c.indexOf('int') > 0
                        dstat.int[c] = {index: i, name: key + c, type: 'scatter', x: [], y: []}
                    if c.indexOf('csw') > 0
                        dstat.csw[c] = {index: i, name: key + c, type: 'scatter', x: [], y: []}

            if is_dstat and line_index > 1
                for stat_name, stat of dstat
                    for stat_k, stat_v of stat
                        stat_v.x.push(columns[0].split(' ')[1])
                        stat_v.y.push(columns[stat_v.index])

        table_html += '</table></div>'
        stat_html += table_html + '</div>'

        for t in tables
            if key.indexOf(t) >= 0
                stats_table_html += stat_html
                break

        for stat_name, stats of dstat_stats_map
            for stat_k, stat_v of dstat[stat_name]
                stats.push(stat_v)

    $('#monitor-stats-table').html(stats_table_html)

    # render graph
    stats_graph_html = ""
    for graph in graphs
        stats_graph_html += "<div class=\"col-xs-6\"><div id=\"#{graph}\"></div></div>"

    $('#monitor-stats-graph').html(stats_graph_html)

    console.log dstat_stats_map
    for graph in graphs
        render_monitor_graph(graph, dstat_stats_map[graph])

render_monitor_graph = (title, stats)->
    layout = {
        'title': title,
        'xaxis': {
            'title': 'timestamp',
            'showgrid': false,
            'zeroline': true,
        },
        'yaxis': {
            'title': title,
            'showline': false,
            'zeroline': true,
        },
    }

    Plotly.newPlot(title, stats, layout)
