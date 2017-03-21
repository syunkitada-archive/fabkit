render_datamap = ->
    datamap = node_cluster.datamap
    for mapname of datamap
        if mapname not in datamap_tabs
            datamap_tabs.push(mapname)

    nav_html = ''
    tabpanels_html = ''
    for mapname in datamap_tabs
        panel_id = "datamap-#{mapname}"
        nav_html += """
        <li role="presentation">
            <a id="map-#{mapname}" class="datamap-tab" href="##{panel_id}" role="tab" data-toggle="tab">#{mapname}</a>
        </li>"""

        tabpanels_html += """
        <div role="tabpanel" class="tab-pane active" id="#{panel_id}">
        </div>
        """

    $('#datamap-nav').html(nav_html)
    $('#datamap-tabpanels').html(tabpanels_html)

bind_shown_tab_event = ->
    $('.datamap-tab').on('shown.bs.tab', (e) ->
        mapname = $(e.target).html()
        panel_id = "datamap-#{mapname}"
        map = node_cluster.datamap[mapname]
        if not map.is_rendered
            console.log "render #{mapname}"
            map.is_rendered = true
            if map.type == 'table'
                render_table_panel(panel_id, map)
            else if map.type == 'partition'
                render_partition_panel(panel_id, map)
            else if map.type == 'force'
                render_force_panel(panel_id, map)
            else if map.type == 'line-chart'
                render_line_chart_panel(panel_id, map)
            else
                console.log map

        return)


render_table_panel = (panel_id, map) ->
    thead_html = ''
    ths = []
    tbody_html = ''
    for tr in map.data
        for th, td of tr
            if ths.indexOf(th) == -1
                ths.push(th)

    ths.sort()
    for th in ths
        th = th.replace(/^![!0-9]/, '')
        thead_html += "<th>#{th}</th>"

    for tr in map.data
        tds = []
        for th, td of tr
            index = ths.indexOf(th)
            if index == -1
                index = ths.length - 1
            tds[index] = td

        tbody_html += '<tr>'
        for td in tds
            tbody_html += "<td>#{td}</td>"

        tbody_html += '</tr>'

    table_html = """
    <div class="table-responsive">
        <table id="datamap-table" class="table table-striped table-bordered tablesorter">
            <thead id="datamap-thead"><tr>#{thead_html}</tr></thead>
            <tbody id="datamap-tbody">#{tbody_html}</tbody>
        </table>
    </div>
    """
    $("##{panel_id}").html(table_html)
    $('#datamap-table').tablesorter({
        sortList: [[0, 0]]
    })


render_line_chart_panel = (panel_id, map) ->
    thead_html = ''
    ths = []
    tbody_html = ''

    yaxis = map.layout.yaxis.title
    xaxis = map.layout.xaxis.title
    tds = []
    ths.push()
    for d, i in map.data
        th = yaxis + '_' + d['!!host']
        ths.push(th)
        if i == 0
            for x in d.x
                tds.push([x])

        for y, i in d.y
            tds[i].push(y)

    ths.splice(0, 0, xaxis)
    for th in ths
        th = th.replace(/^![!0-9]/, '')
        thead_html += "<th>#{th}</th>"

    for td in tds
        tbody_html += "<tr>"
        for t in td
            tbody_html += "<td>#{t}</td>"
        tbody_html += "</tr>"

    graph_id = "#{panel_id}-graph"
    table_html = """
    <div id="#{graph_id}" style="width: 100%"></div>
    <div class="table-responsive">
        <table id="datamap-table" class="table table-striped table-bordered tablesorter">
            <thead id="datamap-thead"><tr>#{thead_html}</tr></thead>
            <tbody id="datamap-tbody">#{tbody_html}</tbody>
        </table>
    </div>
    """
    $("##{panel_id}").html(table_html)

    data = []
    for d in map.data
        trace = {
            x: d.x,
            y: d.y,
            type: 'scatter',
            name: d['!!host'],
        }

        data.push(trace)

    Plotly.newPlot(graph_id, data, map.layout)
