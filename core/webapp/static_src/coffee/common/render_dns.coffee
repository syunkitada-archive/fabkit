render_dns_records = ->
    records_tbody_html = ""
    for record in dns_records
        records_tbody_html += """
            <tr>
                <td>#{record.name}</td>
                <td>#{record.type}</td>
                <td>#{record.content}</td>
                <td>#{record.ttl}</td>
            </tr>"""

    $('#dns-records-tbody').html(records_tbody_html)
