function Timer(options){
    var self = this;
    var _timeout;
    var _callback;
    var defaults = {
        callback: function(){},
        timer: null,    //seconds
        scope: window,
        url: ''
    }
    Ext.apply(this, options, defaults);

    this.updateTime = function(new_time){
        _timeout || clearTimeout(_timeout);
        setTimeout(_callback, new_time*1000);
    };

    this.callNow = function(){
        _callback();
    };

    this.syncWithServer = function(){
        Ext.Ajax.request({
            url: this.url,
            method: 'POST',
            success: function(response){
                var time = +response.responseText;
                if (isNaN(time)){
                    _timeout || clearTimeout(_timeout);
                }else{
                    self.updateTime(time);
                }
            },
            failure: function(){
                Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
            }
        });
    };

    _callback = function(){
        self.callback.call(self.scope);
        self.syncWithServer();
    }

    if (this.timer){
        _timeout = setTimeout(_callback, this.timer*1000);
    }else{
        this.syncWithServer();
    }

}