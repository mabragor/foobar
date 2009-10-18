Ext.ux.SchedulePanel = Ext.extend(Ext.Panel, {
    layout: 'fit',
    frame: true,
    border: false,
    region: 'center',
    title: 'Schedule',
    html: '<div id="calendar"></div>',
    addRoomFilterToolbar: function(store, records){
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
                    fn: this.addRoomFilterToolbar,
                    single: true,
                    scope: this
                }
            }
        });
        this.tbar = [];
        this.fbar = [
            {text: '<<<', handler: function() {this.calendar.weekCalendar('prevWeek')}, scope: this},
            {text: '<', handler: function() {this.calendar.weekCalendar('prevDay')}, scope: this},
            {text: 'today',handler: function() {this.calendar.weekCalendar('today')}, scope: this},
            {text: '>', handler: function() {this.calendar.weekCalendar('nextDay')}, scope: this},
            {text: '>>>',handler: function() {this.calendar.weekCalendar('nextWeek')}, scope: this}
        ];

        
        //-----Cerate event window-----
        this.ce_window = (function(options){
            return new Ext.Window({
                closeAction: 'hide',
                width: 400,
                height: 250,
                constrain: true,
                title: 'Create event',
                layout: 'fit',
                items: new Ext.ux.CreateEventForm({
                    url: options.urls.add_event,
                    items: [{
                            xtype: 'displayfield',
                            hideLabel: true,
                            id: 'course_field'
                        },{
                            xtype: 'displayfield',
                            hideLabel: true,
                            id: 'day_field'
                        },{
                            id: 'time_field',
                            xtype: 'timefield',
                            fieldLabel: 'Start',
                            minValue: options.businessHours.start+':00',
                            maxValue: options.businessHours.end+':00',
                            increment: 60 / options.timeslotsPerHour,
                            format: 'G:i',
                            allowBlank:false,
                            name: 'time'
                        },{
                            xtype: 'combo',
                            fieldLabel: 'Room',
                            triggerAction:'all',
                            allowBlank:false,
                            editable: false,
                            store: this.room_store,
                            valueField: 'id',
                            displayField: 'text',
                            hiddenName: 'room',
                            name: 'room_name'
                        }
                    ]
                }),//Ext.ux.CreateEventForm
                listeners: {
                    show: function(){
                        this.get(0).getForm().reset();
                    }
                }
            });//Ext.Window
        }).call(this, this.c_options);
        //-----------------------------
        Ext.ux.SchedulePanel.superclass.initComponent.call(this);
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
        this.calendar.find(".day-column-inner").each(function(i, dropTarget){
            new Ext.dd.DropTarget(dropTarget, {
                ddGroup:'t2schedule',
                notifyDrop:function(dd, e, node) {
                    var start_date = $(this.getEl()).data("startDate");
                    var form = $self.ce_window.get(0).getForm();
                    form.baseParams = {
                        course: node.node.id
                    };
                    form.begin_day = $(this.getEl()).data("startDate");
                    $self.ce_window.show();
                    form.findField('course_field').setValue(node.node.text);
                    form.findField('day_field').setValue(form.begin_day.format('j.n.Y'));
                    return true;
                }//notifyDrop
            });//Ext.dd.DropTarget
            return true
        });//Ext.each
    }//afterRender
})

Ext.reg('ext:ux:schedule-panel', Ext.ux.SchedulePanel);

Ext.ux.CreateEventForm = Ext.extend(Ext.form.FormPanel, {
    labelWidth: 100,
    frame: true,
    initComponent: function(){
        var config = {
            buttons:[{
                text: 'Submit',
                formBind:true,
                scope:this,
                handler:this.submit
            }]
        }
        Ext.apply(this, Ext.apply(this.initialConfig, config));
        Ext.ux.CreateEventForm.superclass.initComponent.call(this);
    },//initComponent
    onRender: function() {
        Ext.ux.CreateEventForm.superclass.onRender.apply(this, arguments);
        this.getForm().waitMsgTarget = this.getEl();
    },//onRender
    submit: function(){
        var form = this.getForm();
        if (form.isValid()){
            var time_field = form.findField('time_field');
            var time = Date.parseDate(time_field.getValue(), time_field.format);
            form.baseParams.begin = form.begin_day
                .add(Date.HOUR, time.getHours())
                .add(Date.MINUTE, time.getMinutes())
                .format('Y-m-d H:i:s');
            form.submit({
                url: this.url,
                scope: this,
                success: this.onSuccess,
                failure: this.onFailure,
                waitMsg:'Saving...'
            });
        }
    },//submit
    onSuccess: function(form, action){
    }//onSuccess

});