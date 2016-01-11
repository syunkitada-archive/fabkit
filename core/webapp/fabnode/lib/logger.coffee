log4js = require('log4js')
fs = require('fs')

module.exports = {
    init: ()->
        config = global.lib.config

        fs.mkdir 'logs', (err)->
            return

        log4js.configure({
            appenders: [
                { type: 'console', category: 'all' }
                { type: 'file', filename: 'logs/all.log', category: 'all' }
                { type: 'console', category: 'error' }
                { type: 'file', filename: 'logs/error.log', category: 'error' }
            ]
        })

        this.all = log4js.getLogger('all')
        if config.debug
            this.all.setLevel('DEBUG')
        else
            this.all.setLevel('INFO')

        this.error = log4js.getLogger('error')
        this.error.setLevel('ERROR')

        this.all.debug 'logger: initialized'
}
