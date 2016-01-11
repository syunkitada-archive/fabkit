http = require('http')
querystring = require('querystring')


module.exports = {
    request: (socket, path, data, success_handler, error_handler)->
        lib = global.lib
        context = lib.context
        config = lib.config
        logger = lib.logger

        logger.all.debug "webapi: REQ_PATH: #{path}"
        logger.all.debug "webapi: REQ_DATA: #{data}"

        data.sessionid = socket.sessionid
        values = querystring.stringify(data)

        options = {
            host: config.hostname,
            port: config.port,
            path: path,
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': values.length
            }
        }

        req = http.request options, (res)->
            logger.all.debug("webapi: RES_STATUS: #{res.statusCode}")
            logger.all.debug("webapi: RES_HEADERS: #{JSON.stringify(res.headers)}")
            res.setEncoding('utf8')

            res.on 'data', (data)->
                logger.all.debug("webapi: RES_DATA: #{data}")
                success_handler(data)

        req.on 'error', (e)->
            error_handler(e)

        req.write(values)
        req.end()
}
