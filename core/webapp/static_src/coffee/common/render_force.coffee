render_force_panel = (panel_id, map) ->
    console.log panel_id
    console.log map
    id = 'force-svg'
    $("##{panel_id}").html("""
    <div class="graph-svg-wrapper">
        <svg id="#{id}"></svg>
    </div>""")

    nodes = map.data.nodes
    links = map.data.links

    svg = d3.select("##{id}")
    $svg = $("##{id}").empty()
    w = $svg.width()
    h = $svg.height()

    #forceの設定
    force = d3.layout.force()
            .nodes(nodes) #nodesには配列を与える
            .links(links)
            .linkDistance(150)  # ノードとノードのリンクの長さ
            .linkStrength(0.1)  # (1 [0-1]) リンク強度（ノードの引力はリンク強度×リンク数の分だけ強くなる)
            .friction(0.8)  # (0.9 [0-1]) 摩擦力（加速度の減衰力）値を小さくすると収束するまでの加速が小さくなる
            .charge(-300)  # (-30) 推進力（反発力) 負の値だとノード同士が反発し、正の値だと引き合う
            # .chargeDistance(500)
            .gravity(.05)  # (0.1) 重力 画面の中心に動く力
            # .distance(200)
            # theta(0.8)
            .size([w, h])

    link = svg.selectAll('.link')
              .data(links)
              .enter().append('line')
              .attr('class', 'link')
              .attr('marker-end', 'url(#markerArrow)')

    node = svg.selectAll(".node")
              .data(nodes)
              .enter().append('g')
              .attr('class', 'node')
              .call(force.drag)  # nodeのドラッグを可能にする

    node.append('glyph')
        .attr('class', 'glyphicon glyphicon-star')
        .attr('unicode')

    node.append("image")
        .attr("xlink:href", (d) ->
            "/static/vendor/defaulticon/png/#{d.icon}.png")
        .attr("x", 6)
        .attr("y", -34)
        .attr('width', 30)
        .attr('height', 30)

    node.append("circle")
        .attr("r", 6)
        .attr('class', 'node-circle')

    node.append('text')
        .attr('dx', 12)
        .attr('dy', '.35em')
        .attr('class', 'node-label')
        .text((d) -> d.name)

    if mode.current == mode.NODE
        node.append('text')
            .attr('dx', 12)
            .attr('dy', '.35em')
            .attr('y', 16)
            .attr('class', (d) ->
                if d.danger_length > 0
                    return 'node-label-danger'
                if d.warning_length > 0
                    return 'node-label-warning'
                else
                    return 'node-label-success')
            .text((d) -> "✔ #{d.success_length},
                          ▲ #{d.warning_length},
                          ✘ #{d.danger_length}")

    #forceシミュレーションをステップごとに実行
    force.on "tick", (e)->
        link.attr('x1', (d) -> d.source.x)
        link.attr('y1', (d) -> d.source.y)
        link.attr('x2', (d) -> d.target.x)
        link.attr('y2', (d) -> d.target.y)
        node.attr('transform', (d) -> "translate(#{d.x}, #{d.y})")

    #forceシミュレーションの開始
    force.start()
