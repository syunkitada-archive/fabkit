apps.log = (msg)->
    if apps.debug
        if typeof(msg) == 'string'
            console.log msg
        else
            console.dir msg
