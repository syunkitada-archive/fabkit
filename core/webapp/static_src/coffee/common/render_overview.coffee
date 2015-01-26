render_overview_layout = () ->
    id = '#overview-svg'
    nodes = graph_nodes
    links = graph_links

    svg = d3.select(id)
    $svg = $(id).empty()
    w = $svg.width()
    h = $svg.height()
    x = d3.scale.linear().range([0, w])
    y = d3.scale.linear().range([0, h])

    root = {
        type: 'root',
        name: 'fabscript',
        children: graph_nodes,
    }

    vis = d3.select(id)
            .attr("width", w)
            .attr("height", h)

    partition = d3.layout.partition().value((d) -> d.size )

    click = (d) ->
        if !d.children
            return

        kx = (if d.y then w - 40 else w) / (1 - d.y)
        ky = h / d.dx
        x.domain([d.y, 1]).range([(if d.y then 40 else 0), w])
        y.domain([d.x, d.x + d.dx])

        t = g.transition()
            .duration(d3.event.altKey ? 7500 : 750)
            .attr("transform", (d) -> "translate(" + x(d.y) + "," + y(d.x) + ")")

        t.select("rect")
         .attr("width", d.dy * kx)
         .attr("height", (d) -> d.dx * ky)

        t.select("text")
         .attr("transform", transform)
         .style("opacity", (d) ->
             if d.dx * ky > 12 then 1 else 0)

        d3.event.stopPropagation()
        return

    g = vis.selectAll("g")
        .data(partition.nodes(root))
        .enter().append("svg:g")
        .attr("transform", (d) -> "translate(" + x(d.y) + "," + y(d.x) + ")")
        .on("click", click)

    kx = w / root.dx
    ky = h / 1

    g.append("rect")
      .attr("width", root.dy * kx)
      .attr("height", (d) -> d.dx * ky)
      .attr("class", (d) -> if d.children then "#{d.class} parent" else d.class)

    transform = (d) ->
        "translate(8," + d.dx * ky / 2 + ")"

    g.append("text")
        .attr("transform", transform)
        .attr("dy", ".35em")
        .style("opacity", (d) ->
            if d.dx * ky > 12 then 1 else 0)
        .text((d) -> return "#{d.name}")

    g.append("text")
        .attr("transform", transform)
        .attr("dy", ".35em")
        .attr("y", 15)
        .style("opacity", (d) ->
            if d.dx * ky > 12 then 1 else 0)
        .text((d) ->
            if d.type == 'root'
                success_length = 0
                warning_length = 0
                danger_length = 0
                for fabscript in d.children
                    success_length += fabscript.success_length
                    warning_length += fabscript.warning_length
                    danger_length += fabscript.danger_length

                return "✔ #{success_length}, ▲ #{warning_length}, ✘ #{danger_length}"
            if d.type == 'fabscript'
                return "✔ #{d.success_length}, ▲ #{d.warning_length}, ✘ #{d.danger_length}"
            else if d.type == 'status'
                return "( #{d.length} )"
            )

    d3.select(window).on("click", -> click(root))
