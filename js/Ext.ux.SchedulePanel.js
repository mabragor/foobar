Ext.ux.SchedulePanel = Ext.extend(Ext.Panel, {
    layout: 'fit',
    frame: true,
    border: false,
    region: 'center',
    title: 'Schedule',
    html: '<div id="calendar"></div>',
    addRoomFilterToolbar: function(store){
        var $self = this;
        var toolbar = this.getTopToolbar();
        store.each(function(item){
            this.addButton({
                enableToggle: true,
                hideLabel: true,
                pressed: true,
                text: item.data.text,
                room_id: item.data.id,
                handler: $self.filterRoomHandler,
                scope: $self
            });
        }, toolbar);
        toolbar.doLayout();
    },
    addRoomButtonsToForm: function(store){
        var form = this.ce_window.get(0);
        var button_group = this.ce_window.get(0).findById('rooms_group');
        store.each(function(item){
            this.addButton({
                hideLabel: true,
                text: item.data.text,
                room_id: item.data.id,
                handler: form.submit,
                scope: form
            });
        }, button_group);
    },
    filterRoomHandler: function(button, event){
        var toolbar = this.getTopToolbar();
        var rooms = []
        toolbar.items.each(function(item){
            if(item.pressed){
                rooms.push(item.room_id);
            }
        });
        this.calendar.weekCalendar('filterByParam', {rooms: rooms});
    },
    initComponent: function(){
        this.room_store = new Ext.data.JsonStore({
            id:'id',
            root: 'rows',
            autoLoad: true,
            fields:[
                {name:'id', type:'int'},
                {name:'color', type:'string'},
                {name:'text', type:'string'}
            ],
            //url:this.c_options.urls.get_rooms,
            proxy: new Ext.data.HttpProxy({
                method: 'POST',
                url: this.c_options.urls.get_rooms
            }),
            listeners: {
                load:{
                    fn: function(s){this.addRoomFilterToolbar(s);this.addRoomButtonsToForm(s)},
                    single: true,
                    scope: this
                }
            }
        });
        this.tbar = [];
        this.fbar = [
            {text: 'Copy',handler: function() {this.status_window.show()}, scope: this},
            {text: '<<<', handler: function() {this.calendar.weekCalendar('prevWeek')}, scope: this},
            {text: '<', handler: function() {this.calendar.weekCalendar('prevDay')}, scope: this},
            {text: 'today',handler: function() {this.calendar.weekCalendar('today')}, scope: this},
            {text: '>', handler: function() {this.calendar.weekCalendar('nextDay')}, scope: this},
            {text: '>>>',handler: function() {this.calendar.weekCalendar('nextWeek')}, scope: this}
        ];

        Ext.ux.SchedulePanel.superclass.initComponent.call(this);
        this.initCreateEventWindow();
        this.initStatusWindow();
    },
    initStatusWindow: function(){
        var coach_store = new Ext.data.JsonStore({
            id:'id',
            root: 'rows',
            fields:[
                {name:'id', type:'int'},
                {name:'name', type:'string'}
            ],
            proxy: new Ext.data.HttpProxy({
                method: 'POST',
                url: this.urls.get_coach_list
            }),
            autoLoad: true
        });
        var form = new Ext.form.FormPanel({
            urls: this.urls,
            labelWidth: 100,
            frame: true,
            items: [{
                    xtype: 'hidden',
                    name: 'id'
                },{
                    xtype: 'displayfield',
                    hideLabel: true,
                    value: 'Course title',
                    name: 'title'
                },{
                    xtype: 'displayfield',
                    hideLabel: true,
                    value: 'Course date',
                    name: 'date'
                },{
                    xtype: 'radiogroup',
                    fieldLabel: 'Status',
                    items: [
                        {boxLabel: 'Done', name: 'status', inputValue: 1, checked: true},
                        {boxLabel: 'Canceled', name: 'status', inputValue: 2}
                    ]
                },{
                    xtype:'fieldset',
                    checkboxToggle:true,
                    title: 'Change coach',
                    autoHeight:true,
                    defaults: {width: 210},
                    defaultType: 'textfield',
                    collapsed: true,
                    checkboxName: 'change_flag',
                    items :[{
                        xtype: 'combo',
                        fieldLabel: 'New coach',
                        valueField:'id',
                        hiddenName:'change',
                        displayField:'name',
                        store: coach_store,
                        triggerAction:'all',
                        minChars: 4,
                        forceSelection:true,
                        disableKeyFilter: true
                    },{
                        xtype: 'checkbox',
                        fieldLabel: 'Outside change',
                        name: 'outside',
                        listeners: {
                            check: function(checkbox, checked){
                                if(checked){
                                    checkbox.ownerCt.get(0).disable();
                                }else{
                                    checkbox.ownerCt.get(0).enable();
                                }
                            }
                        }//listeners
                  }]//fieldset items
             }],//items
             buttons: [{
                 text: 'submit',
                 handler: function(){
                     var form = this.findParentByType('form');
                     form.getForm().submit({
                         url: form.urls.save_event_status,
                         success: function(form, action){
                            action.result.msg && Ext.ux.msg(action.result.msg, '', Ext.MessageBox.INFO);
                            form.load_event()
                        },
                         failure: function(form, action){
                            switch (action.failureType) {
                                case Ext.form.Action.CONNECT_FAILURE:
                                    Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
                                    break;
                                case Ext.form.Action.SERVER_INVALID:
                                    Ext.ux.msg('Failure', action.result.errors, Ext.Msg.ERROR);
                           }//failure
                        }
                     });
                 }
             }],//buttons
             load_event: function(){
                 this.load({
                     url: this.urls.get_unstatus_event,
                     failure: function(form, action) {
                         switch (action.failureType) {
                             case Ext.form.Action.CONNECT_FAILURE:
                                 Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
                                 break;
                             case Ext.form.Action.SERVER_INVALID:
                                 Ext.ux.msg('Failure', action.result.errors, Ext.Msg.ERROR);
                                 action.result.end && form.hide();
                        }
                     }//failure
                 });//form.load
             }
        });
        this.status_window = new Ext.Window({
            closeAction: 'hide',
            width: 400,
            height: 400,
            draggable: false,
            title: 'Event status',
            layout: 'fit',
            autoScroll: true,
            modal: true,
            items: form,//Ext.form.FormPanel
            listeners: {
                 beforeshow: function(window){
                     var form = window.get(0);
                     form.load_event();
                 }
            }//listeners
        });//Ext.Window
    },
    initCreateEventWindow: function(){
        var options = this.c_options;
        this.ce_window = new Ext.Window({
                closeAction: 'hide',
                width: 400,
                height: 250,
                constrain: true,
                title: 'Create event',
                layout: 'fit',
                items: new Ext.ux.CreateEventForm({
                    url: options.urls.add_event,
                    items: [{
                            xtype: 'fieldset',
                            id: 'rooms_group1',
                            title: 'Event information',
                            autoWidth: true,
                            autoHeight: true,
                            items: [{
                                xtype: 'displayfield',
                                hideLabel: true,
                                id: 'course_field'
                            },{
                                xtype: 'displayfield',
                                hideLabel: true,
                                id: 'day_field'
                            }]
                        },{
                            xtype: 'fieldset',
                            id: 'rooms_group',
                            title: 'Chose room',
                            autoWidth: true,
                            autoHeight: true,
                            buttonAlign: 'center',
                            html: '&nbsp;',
                            bodyCssClass: 'room-fieldset-body'
                        }]
                }),//Ext.ux.CreateEventForm
                listeners: {
                    show: function(){
                        this.get(0).getForm().reset();
                    }
                }
            });//Ext.Window
    },
    afterRender: function(){
        Ext.ux.SchedulePanel.superclass.afterRender.call(this);
        //FIXME: change options gathering for calendar
        
        this.c_options.height = function(calendar) {
            return calendar.height();
        };
        this.calendar = $(this.body.dom).weekCalendar(this.c_options);
        this.ce_window.get(0).getForm().on('actioncomplete', function(form, action){
            this.ce_window.hide();
            this.calendar.weekCalendar("updateEvent", action.result.obj);
        }, this)
        var $self = this;
        //Add droping from course's tree'
        //FIXME: rewrite to Ext.each with scope=$self
        var $calendar = this.calendar;
        this.calendar.find(".day-column-inner").each(function(i, dropTarget){
            new Ext.dd.DropTarget(dropTarget, {
                ddGroup:'t2schedule',
                notifyDrop:function(dd, e, node) {
                    
                    if($(this.getEl()).data("startDate") < (new Date()).add(Date.DAY, -1)){
                        return false;
                    }
                    var start_date = $calendar.weekCalendar('getClickTime', e.getPageY() - this.el.getTop(), $(this.getEl()));
                    var form = $self.ce_window.get(0).getForm();
                    form.baseParams = {
                        course: node.node.id,
                        begin: start_date.format('Y-m-d H:i:s')
                    };
                    $self.ce_window.show();
                    form.findField('course_field').setValue(node.node.text);
                    form.findField('day_field').setValue(start_date.format('Y-m-d H:i:s'));
                    return true;
                }//notifyDrop
            });//Ext.dd.DropTarget
            return true
        });//Ext.each
    }//afterRender
});

Ext.reg('ext:ux:schedule-panel', Ext.ux.SchedulePanel);

Ext.ux.CreateEventForm = Ext.extend(Ext.form.FormPanel, {
    labelWidth: 100,
    frame: true,
    onRender: function() {
        Ext.ux.CreateEventForm.superclass.onRender.apply(this, arguments);
        this.getForm().waitMsgTarget = this.getEl();
    },//onRender
    submit: function(button){
        var form = this.getForm();
        if (form.isValid()){
            form.submit({
                url: this.url,
                scope: this,
                success: this.onSuccess,
                failure: this.onFailure,
                waitMsg:'Saving...',
                params: {
                    room: button.room_id
                }
            });
        }
    },//submit
    onSuccess: function(form, action){
        Ext.ux.msg(action.result.msg, '', Ext.MessageBox.INFO);
    },//onSuccess
    onFailure: function(form, action){
        switch (action.failureType) {
            case Ext.form.Action.CONNECT_FAILURE:
                Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
                break;
            case Ext.form.Action.SERVER_INVALID:
                Ext.ux.msg('Failure', action.result.errors, Ext.Msg.ERROR);
       }
    }

});