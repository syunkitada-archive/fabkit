render_force_layout = () ->
    id = '#graph-svg'
    nodes = graph_nodes
    links = graph_links

    svg = d3.select(id)
    $svg = $(id).empty()
    w = $svg.width()
    h = $svg.height()

    #forceの設定
    force = d3.layout.force()
            .nodes(nodes) #nodesには配列を与える
            .links(links)
            .linkDistance(200)  # ノードとノードのリンクの長さ
            .linkStrength(0)  # (1 [0-1]) リンク強度（ノードの引力はリンク強度×リンク数の分だけ強くなる)
            .friction(0.8)  # (0.9 [0-1]) 摩擦力（加速度の減衰力）値を小さくすると収束するまでの加速が小さくなる
            .charge(-300)  # (-30) 推進力（反発力) 負の値だとノード同士が反発し、正の値だと引き合う
            # .chargeDistance(500)
            .gravity(.04)  # (0.1) 重力 画面の中心に動く力
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

    node.append("circle")
        .attr("r", 5)
        .style("fill", "green")

    node.append('text')
        .attr('dx', 12)
        .attr('dy', '.35em')
        .text((d) -> d.name)

    #forceシミュレーションをステップごとに実行
    force.on "tick", (e)->
        link.attr('x1', (d) -> d.source.x)
        link.attr('y1', (d) -> d.source.y)
        link.attr('x2', (d) -> d.target.x)
        link.attr('y2', (d) -> d.target.y)
        node.attr('transform', (d) -> "translate(#{d.x}, #{d.y})")

    #forceシミュレーションの開始
    force.start()
