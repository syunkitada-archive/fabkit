render_force_layout = (id, nodes, links) ->
    svg = d3.select(id)
    $svg = $(id)
    w = $svg.width()
    h = $svg.height()

    #forceの設定
    force = d3.layout.force()
            .nodes(nodes) #nodesには配列を与える
            .links(links)
            .gravity(.05)
            .distance(100)
            .charge(-100)
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
