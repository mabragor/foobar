Ext.ux.CopyHandler = Ext.extend(Ext.Window, {
    title: 'Chose week to paste',
    html: 'Week should be empty and in the future.',
    hidden: true,
    width: 250,
    height: 100,
    border: false,
    closeAction: 'hide',
    constrainHeader: true,
    plain: true,
    resizable: false,
    bodyStyle: {'fontSize': '13px', 'textAlign': 'center'},
    //margins: '5px 0 0 0',
    closable: false,
    x: 100,
    y: 25,
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
            pasteMessageTemplate: (new Ext.Template('Paste events from {0:date}-{1:date} to {2:date}-{3:date}?')).compile(),
            copyMessageTemplate: (new Ext.Template('Copy events from {0:date}-{1:date}?')).compile()
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
        this._from = {
            start: weekStartDate,
            end: weekEndDate
        }
        var text = this.copyMessageTemplate.apply([this._from.start, this._from.end]);
        Ext.Msg.confirm('Copy', text, this.copy, this);
    },
    copy: function(button){
        if (button == 'yes'){
            this.show();
        }
    },
    pasteButtonHandler: function(){
        this.calendar.weekCalendar('startWeek', this.pastHandler.createDelegate(this));
    },
    pastHandler: function(data, weekStartDate, weekEndDate){
        if (data.length){
            Ext.ux.msg('Week must be empty', '', Ext.Msg.WARNING);
        }//TODO: set code here, after testing serverside validation
        this._to = {
            start: weekStartDate,
            end: weekEndDate
        };
        var text = this.pasteMessageTemplate.apply([this._from.start, this._from.end, this._to.start, this._to.end]);
        Ext.Msg.confirm('Paste', text, this.paste, this);
    },
    paste: function(button){
        if (button == 'yes'){
            Ext.ux.msg('Coping events!', '', Ext.Msg.INFO);
        }
        this.hide();
    },
    hide: function(){
        this._from = null;
        this._to = null;
        Ext.ux.CopyHandler.superclass.hide.call(this);
    }
});