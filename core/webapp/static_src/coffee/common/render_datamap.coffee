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
            map.is_rendered = true
            if map.type == 'table'
                render_table_panel(panel_id, map)
            if map.type == 'partition'
                render_partition_panel(panel_id, map)

        return)


render_map = ->
    console.log 'test'


render_table_panel = (panel_id, map) ->
    thead_html = '<tr>'
    for td in map.head
        thead_html += "<th>#{td}</th>"
    thead_html += '</tr>'

    tbody_html = ''
    for tr in map.body
        tr_html = '<tr>'
        console.log tr
        for td in tr
            tr_html += "<td>#{td}</td>"
        tr_html += '</tr>'
        tbody_html += tr_html

    table_html = """
    <table id="datamap-table" class="table table-striped table-bordered tablesorter">
        <thead id="datamap-thead">#{thead_html}</thead>
        <tbody id="datamap-tbody">#{tbody_html}</tbody>
    </table>
    """
    $("##{panel_id}").html(table_html)
    $('#datamap-table').tablesorter({
        sortList: [[0, 0]]
    })
