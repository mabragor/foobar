Ext.ux.SchedulePanel = Ext.extend(Ext.Panel, {
    layout: 'fit',
    frame: true,
    border: false,
    region: 'center',
    title: 'Schedule',
    initComponent: function(){
        Ext.ux.SchedulePanel.superclass.initComponent.call(this);
    // $(this.body.dom).weekCalendar(jQuery.extend(options, calendar_options));
    },
    afterRender: function(){
        Ext.ux.SchedulePanel.superclass.afterRender.call(this);
        $(this.body.dom).weekCalendar(jQuery.extend(options, calendar_options));
    }
})

Ext.reg('ext:ui:schedule-panel', Ext.ux.SchedulePanel);
