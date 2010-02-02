Ext.ux.CopyHandler = Ext.extend(Ext.Window, {
    title: '',
    html: 'Chose week to paste. Week should be empty and in the future.',
    hidden: true,
    width: 250,
    height: 150,
    border: false,
    constrainHeader: true,
    plain: true,
    bodyStyle: {'fontSize': '13px'},
    //margins: '5px 0 0 0',
    x: 100,
    y: 25,
    pasteMessageTemplate: (new Ext.Template('Paste events from {0:date}-{1:date} to {2:date}-{3:date}?')).compile(),
    copyMessageTemplate: (new Ext.Template('Copy events from {0:date}-{1:date}?')).compile(),
    titleTemplate: (new Ext.Template('Coping events from {0:date}-{1:date}?')).compile(),
    initComponent: function(){
        var config = {
            buttons: [{
                text: 'Cancel',
                handler: this.hide,
                scope: this
            },{
                text: 'Paste',
                handler: this.pasteButtonHandler,
                scope: this
            }],
            closable: false,
            resizable: false,
            closeAction: 'hide'
        }
        Ext.apply(this, config);
        Ext.ux.CopyHandler.superclass.initComponent.call(this);
        this._from = null;
        this._to = null;
    },
    copyButtonHandler: function(){
        this.calendar.weekCalendar('startWeek', this.copyHandler.createDelegate(this));
    },
    copyHandler: function(data, weekStartDate, weekEndDate){
        if (data.length){
            this._from = {
                start: weekStartDate,
                end: weekEndDate
            }
            var text = this.copyMessageTemplate.apply([this._from.start, this._from.end]);
            Ext.Msg.confirm('Copy', text, this.copy, this);
        }else{
            Ext.ux.msg('Nothing to copy.', '', Ext.Msg.WARNING);
        }

    },
    copy: function(button){
        if (button == 'yes'){
            this.setTitle(this.titleTemplate.apply([this._from.start, this._from.end]));
            this.show();
        }
    },
    pasteButtonHandler: function(){
        this.calendar.weekCalendar('startWeek', this.pastHandler.createDelegate(this));
    },
    pastHandler: function(data, weekStartDate, weekEndDate){
        if (data.length){
            Ext.ux.msg('Week must be empty.', '', Ext.Msg.WARNING);
        }else if(weekStartDate < Date.now()){
            Ext.ux.msg('Can not paste events into the past.', '', Ext.Msg.WARNING);
        }else if(weekStartDate == this._from.start){
            Ext.ux.msg('Copy to the same week.', '', Ext.Msg.WARNING);
        }else{
            this._to = {
                start: weekStartDate,
                end: weekEndDate
            };
            var text = this.pasteMessageTemplate.apply([this._from.start, this._from.end, this._to.start, this._to.end]);
            Ext.Msg.confirm('Paste', text, this.paste, this);
        }
    },
    paste: function(button){
        if (button == 'yes'){
            Ext.Ajax.request({
                url: this.url,
                method: 'POST',
                params: {
                    from_date: this._from.start.format('Y-m-d'),
                    to_date: this._to.start.format('Y-m-d')
                },
                success: (function(response){
                    var result = Ext.util.JSON.decode(response.responseText);
                    if (result.success){
                        Ext.ux.msg('Events copied success.', '', Ext.Msg.INFO);
                        this.hide();
                        this.calendar.weekCalendar('refresh');
                    }else{
                        Ext.ux.msg('Error.', result.errors, Ext.Msg.WARNING);
                    }
                }).createDelegate(this)
            });
        }
    },
    hide: function(){
        this._from = null;
        this._to = null;
        Ext.ux.CopyHandler.superclass.hide.call(this);
    }
});