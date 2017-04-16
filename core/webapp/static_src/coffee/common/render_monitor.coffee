refresh_monitor = (is_auto_refresh=false) ->
    console.log 'refresh_monitor'
    console_url = "/node/#{current_cluster}/get_console/"
    $.getJSON(console_url, (data) ->
        render_monitor(data)

        if is_auto_refresh
            refresh_interval = parseInt($('#monitor-refresh-interval').val()) * 1000
            setTimeout(refresh_monitor, refresh_interval, is_auto_refresh=is_auto_refresh)
    )

render_monitor = (data) ->
    console.log 'Render data'
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
        procs: [],
        int: [],
        csw: [],
        mem: [],
        vm: [],
        io_read: [],
        io_writ: [],
        disk_read: [],
        disk_writ: [],
        net_recv: [],
        net_send: [],
        tcp_sockets: [],
        sockets: [],
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
            procs: {},
            int: {},
            csw: {},
            mem: {},
            vm: {},
            io_read: {},
            io_writ: {},
            disk_read: {},
            disk_writ: {},
            net_recv: {},
            net_send: {},
            tcp_sockets: {},
            sockets: {},
        }
        for line, line_index in lines
            columns = line.split(',')
            table_html += '<td>' + columns.join('</td><td>') + '</td></tr>'

            if is_dstat and line_index == 0
                for c, i in columns
                    if c.indexOf('net/') > 0
                        dstat.net_recv[c] = {index: i  , name: key + c + '.recv', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.net_send[c] = {index: i+1, name: key + c + '.send', type: 'scatter', x: [], y: [], chart_data: []}

                    else if c.indexOf('procs') > 0
                        dstat.procs['run'] = {index: i  , name: key + c + '.run', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.procs['blk'] = {index: i+1, name: key + c + '.blk', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.procs['new'] = {index: i+2, name: key + c + '.new', type: 'scatter', x: [], y: [], chart_data: []}

                    else if c.indexOf('memory usage') > 0
                        dstat.mem['used'] = {index: i  , name: key + c + '.used', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.mem['buff'] = {index: i+1, name: key + c + '.buff', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.mem['cach'] = {index: i+2, name: key + c + '.cach', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.mem['free'] = {index: i+3, name: key + c + '.free', type: 'scatter', x: [], y: [], chart_data: []}
                    else if c.indexOf('virtual memory') > 0
                        dstat.vm['majpf'] = {index: i  , name: key + c + '.majpf', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.vm['minpf'] = {index: i+1, name: key + c + '.minpf', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.vm['alloc'] = {index: i+2, name: key + c + '.alloc', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.vm['free']  = {index: i+3, name: key + c + '.free',  type: 'scatter', x: [], y: [], chart_data: []}

                    else if c.indexOf('io/') > 0
                        dstat.io_read[c] = {index: i  , name: key + c + '.read', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.io_writ[c] = {index: i+1, name: key + c + '.writ', type: 'scatter', x: [], y: [], chart_data: []}

                    else if c.indexOf('dsk/') > 0
                        dstat.disk_read[c] = {index: i  , name: key + c + '.read', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.disk_writ[c] = {index: i+1, name: key + c + '.writ', type: 'scatter', x: [], y: [], chart_data: []}

                    else if c.indexOf('tcp sockets') > 0
                        dstat.tcp_sockets['lis'] = {index: i  , name: key + c + '.lis', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.tcp_sockets['act'] = {index: i+1, name: key + c + '.act', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.tcp_sockets['syn'] = {index: i+2, name: key + c + '.syn', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.tcp_sockets['tim'] = {index: i+3, name: key + c + '.tim', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.tcp_sockets['clo'] = {index: i+4, name: key + c + '.clo', type: 'scatter', x: [], y: [], chart_data: []}

                    else if c.indexOf('sockets') > 0
                        dstat.sockets['tot'] = {index: i  , name: key + c + '.tot', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.sockets['tcp'] = {index: i+1, name: key + c + '.tcp', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.sockets['udp'] = {index: i+2, name: key + c + '.udp', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.sockets['raw'] = {index: i+3, name: key + c + '.raw', type: 'scatter', x: [], y: [], chart_data: []}
                        dstat.sockets['frg'] = {index: i+4, name: key + c + '.frg', type: 'scatter', x: [], y: [], chart_data: []}

            if is_dstat and line_index == 1
                for c, i in columns
                    if c.indexOf('int') > 0
                        dstat.int[c] = {index: i, name: key + c, type: 'scatter', x: [], y: [], chart_data: []}
                    if c.indexOf('csw') > 0
                        dstat.csw[c] = {index: i, name: key + c, type: 'scatter', x: [], y: [], chart_data: []}

            if is_dstat and line_index > 1
                for stat_name, stat of dstat
                    for stat_k, stat_v of stat
                        # x = columns[0].split(' ')[1]
                        tmp_x = columns[0].split(' ')
                        tmp_x2 = tmp_x[0].split('-')
                        x = "#{tmp_x2[1]}-#{tmp_x2[0]} #{tmp_x[1]}"

                        y = columns[stat_v.index]
                        stat_v.x.push(x)
                        stat_v.y.push(y)
                        stat_v.chart_data.push({
                            x: x,
                            y: y,
                        })

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

    height = 300

    # render graph
    stats_graph_width = $('#monitor-stats-graph').width()
    lines = 1
    div_class = 'col-xs-12'
    if stats_graph_width >= 1600
        lines = 3
        div_class = 'col-xs-4'
    else if stats_graph_width >= 1200
        lines = 2
        div_class = 'col-xs-6'
    else if stats_graph_width >= 800
        lines = 1
        div_class = 'col-xs-6'

    canvas_width = Math.floor(stats_graph_width / lines)

    stats_graph_html = ""
    for i in [0...lines]
        stats_graph_html += "<div id=\"graph-row#{i}\" class=\"#{div_class}\"></div>"

    $('#monitor-stats-graph').html(stats_graph_html)

    line_index = 0
    max_line = lines - 1
    for graph in graphs
        $("#graph-row#{line_index}").append("<div><canvas id=\"#{graph}\" style=\"width: #{canvas_width}px; height: 200px;\"></canvas><div id=\"#{graph}-legend\"></div></div>")
        # $("#graph-row#{line_index}").append("<div><div id=\"#{graph}\"></div></div>")

        if line_index == max_line
            line_index = 0
        else
            line_index += 1

    window.chart_map = {}

    for graph in graphs
        render_monitor_chart(graph, dstat_stats_map[graph])
        # render_monitor_graph(graph, dstat_stats_map[graph])


render_monitor_chart = (id, stats)->
    datasets = []
    colors = [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 206, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)',
        'rgba(153, 102, 255, 0.5)',
        'rgba(255, 159, 64, 0.5)'
    ]
    colors_index = 0
    colors_max_index = colors.length - 1
    for stat in stats
        color = colors[colors_index]
        datasets.push({
          label: stat.name,
          data: stat.chart_data,
          borderColor: color,
          fill: false,
        })

        if colors_index == colors_max_index
            colors_index = 0
        else
            colors_index += 1

    window.apps.updateDataset = (e, id, datasetIndex) ->
        index = datasetIndex
        ci = window.chart_map[id]
        meta = ci.getDatasetMeta(index)
        if meta.hidden == null
            meta.hidden = true
        else
            meta.hidden = null

        ci.update()

    options = {
        title: {
            display: true,
            text: id,
        },
        # tooltips: {
        #   mode: 'label'
        # },
        scales: {
            xAxes: [{
                type: "time",
            }],
        },
        responsive: true,
        legend: {
            display: false,
        },
        legendCallback: (chart) ->
            text = []

            text.push('<ul class=\"chart-legend\">')
            for data, i in chart.data.datasets
                text.push("<li class=\"chart-legend-label-text\" onclick=\"apps.updateDataset(event, '#{id}', #{chart.legend.legendItems[i].datasetIndex})\">")
                text.push("<span style=\"background-color: #{data.borderColor}\">#{data.label}</span>")
                text.push('</li>')

            text.push('</ul>')

            return text.join("")

    }

    console.log(datasets)

    ctx = $("##{id}")
    myChart = new Chart(ctx, {
      type: 'line',
      data: {
        # labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
        datasets: datasets,
      },
      options: options,
    })

    window.chart_map[id] = myChart

    $("##{id}-legend").html(myChart.generateLegend())

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
        legend: {
            orientation: "h"
        }
    }

    Plotly.newPlot(title, stats, layout)
