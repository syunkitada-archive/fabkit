render_datamap = ->
    datamap = node_cluster.datamap
    for mapname of datamap
        if mapname not in datamap_tabs
            datamap_tabs.push(mapname)

    console.log 'render DEBUG'
    nav_html = ''
    for mapname in datamap_tabs
        panel_id = "#datamap-#{datamap[mapname].type}-panel"
        nav_html += """
        <li role="presentation">
            <a id="map-#{mapname}" class="datamap-tab" href="#{panel_id}" role="tab" data-toggle="tab">#{mapname}</a>
        </li>"""

    $('#datamap-nav').html(nav_html)
    $('.datamap-tab').on('shown.bs.tab', (e) ->
        mapname = $(e.target).html()
        map = node_cluster.datamap[mapname]
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

        console.log tbody_html
        $('#datamap-thead').html(thead_html)
        $('#datamap-tbody').html(tbody_html)
        console.log map
        console.log $('#datamap-table')
        console.log $('#node-table')
        $('#datamap-table').tablesorter({
            sortList: [[0, 0]]
        })

        return)


render_map = ->
    console.log 'test'
