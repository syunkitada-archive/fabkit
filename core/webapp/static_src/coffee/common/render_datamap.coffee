# XXX statusmap, relationmapを切り替えるとバグる
# XXX datamapのタブ情報がリセットされない
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

        return)


render_table_panel = (panel_id, map) ->
    thead_html = ''
    ths = []
    tbody_html = ''
    for tr in map.data
        tds = []
        for th, td of tr
            index = ths.indexOf(th)
            if index == -1
                thead_html += "<th>#{th}</th>"
                ths.push(th)
                index = ths.length - 1
            tds[index] = td

        tbody_html += '<tr>'
        for td in tds
            tbody_html += "<td>#{td}</td>"

        tbody_html += '</tr>'

    table_html = """
    <table id="datamap-table" class="table table-striped table-bordered tablesorter">
        <thead id="datamap-thead"><tr>#{thead_html}</tr></thead>
        <tbody id="datamap-tbody">#{tbody_html}</tbody>
    </table>
    """
    $("##{panel_id}").html(table_html)
    $('#datamap-table').tablesorter({
        sortList: [[0, 0]]
    })
