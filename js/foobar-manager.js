Ext.onReady(function() {
    Ext.QuickTips.init();
    Ext.ux.msg = function(){
        var msgCt;
        function createBox(title, text, type){
            return ['<div class="msg">',
                    '<div class="x-box-tl"><div class="x-box-tr"><div class="x-box-tc"></div></div></div>',
                    '<div class="x-box-ml"><div class="x-box-mr"><div class="x-box-mc">',
                    '<div class="ext-mb-icon ', type ,'">',
                    '<h3>', title, '</h3>', text,
                    '</div></div></div></div>',
                    '<div class="x-box-bl"><div class="x-box-br"><div class="x-box-bc"></div></div></div>',
                    '</div>'].join('');
        }
        
        return function(title, text, type){
            if(!msgCt){
                msgCt = Ext.DomHelper.insertFirst(document.body, {id:'msg-div'}, true);
            }
            msgCt.alignTo(document, 't-t');
            var m = Ext.DomHelper.append(msgCt, {html:createBox(title, text, type)}, true);
            m.slideIn('t').pause(2).ghost("t", {remove:true});
        }
    }();
    Ext.Ajax.on('requestexception', function(){
        Ext.ux.msg('Failure', 'Ajax communication failed', Ext.Msg.ERROR);
    }, this);

    var panel = new Ext.Viewport({
        title: Ext.getDom('page-title').innerHTML,
        id: 'main',
        layout: 'border',
        //autoHeight: true,
        //height: 600,
        renderTo: Ext.getBody(),
        items: [{
            xtype: 'ext:ux:schedule-panel',
            c_options: schedule_options,
            urls: {
                get_coach_list: URLS.get_coach_list,
                get_unstatus_event: URLS.get_unstatus_event,
                save_event_status: URLS.save_event_status,
                copy_week: URLS.copy_week
            }
        },{
            region: 'west',
            layout: 'vbox',
            frame: true,
            border: false,
            width: '30%',
            split: true,
            collapsible: true,
            collapseMode: 'mini',
            layoutConfig: {
                align : 'stretch',
                pack  : 'start'
            },
            items: [{
                xtype: 'ext:ux:user-panel',
                URLS: {
                    get_user_courses: URLS.get_user_courses,
                    del_user_course: URLS.del_user_course,
                    add_user_course: URLS.add_user_course,
                    get_user_data: '/ajax/rfid/'
                }
            },{
                xtype: 'ext:ux:course-panel',
                dataUrl: URLS.get_course_tree
            }]
        }]
    });

    new Timer({
        callback: function(){
            Ext.getCmp('status_window').show_window();
        },
        url: URLS.get_status_timer
    });
});
