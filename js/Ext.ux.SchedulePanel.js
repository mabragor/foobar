Ext.ux.SchedulePanel = Ext.extend(Ext.Panel, {
    layout: 'fit',
    frame: true,
    border: false,
    region: 'center',
    title: 'Schedule',
    initComponent: function(){
        this.room_store = new Ext.data.JsonStore({
            id:'id',
            root: 'rows',
            fields:[
                {name:'id', type:'int'},
                {name:'color', type:'string'},
                {name:'text', type:'string'}
            ],
            url:this.c_options.urls.get_rooms
        });

        //-----Cerate event window-----
        this.ce_window = (function(options){
            return new Ext.Window({
                closeAction: 'hide',
                width: 500,
                height: 300,
                title: 'Create event',
                layout: 'fit',
                items: new Ext.ux.CreateEventForm({
                    url: options.urls.add_event,
                    items: [{
                            xtype: 'displayfield',
                            hideLabel: true,
                            value: 'Some course'
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
                })//Ext.ux.CreateEventForm
            });//Ext.Window
        }).call(this, this.c_options);
        //-----------------------------
        Ext.ux.SchedulePanel.superclass.initComponent.call(this);
    },
    afterRender: function(){
        Ext.ux.SchedulePanel.superclass.afterRender.call(this);
        //FIXME: change options gathering for calendar
        this.c_options.height = function(calendar) {
            return $(window).height() - $("h1").outerHeight();
        };
        this.calendar = $(this.body.dom).weekCalendar(this.c_options);
        this.ce_window.get(0).getForm().on('actioncomplete', function(form, action){
            this.calendar.weekCalendar("updateEvent", action.result.obj);
            this.ce_window.close();
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