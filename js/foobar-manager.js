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

    // This form shows information about current client. Manager may check
    // client's data, add new courses to client account, take subcharge
    // from him.
    var client_form = new Ext.form.FormPanel({
        standardSubmit: true,
        labelWidth: 100,
        frame: false,
        defaults: {
            style: {width: '100%'}
        },
        items:[
            new Ext.form.TextField({ name: 'first_name', fieldLabel: 'First name', allowBlank: false }),
            new Ext.form.TextField({ name: 'last_name', fieldLabel: 'Last name', allowBlank: false }),
            new Ext.form.TextField({ name: 'email', fieldLabel: 'E-mail', allowBlank: false })
        ],
        buttons: [
            { text: 'Surchange', handler: function() {} },
            { text: 'Assign', handler: function() {} },
            { text: 'Apply', handler: function() {} },
        ]
    });

    var course_store = new Ext.data.JsonStore({
        storeId: 'UserCourses',
        //autoLoad: true,
        autoDestroy: true, // destroy store when the component the store is bound to is destroyed
        root: 'courses', // get data from this key
        idProperty: 'id',
        fields: [
            {name: 'id', type: 'int'},
            'title',
            {name: 'reg_date', type: 'date'},
            {name: 'exp_date', type: 'date'},
            {name: 'count', type: 'int'},
            {name: 'course_id', type: 'int'},
            {name: 'deleteable', type: 'boolean'}
        ],
        proxy: new Ext.data.HttpProxy({
            method: 'POST',
            url: URLS.get_user_courses
        })
    });

    var panel = new Ext.Viewport({
        title: Ext.getDom('page-title').innerHTML,
        id: 'main',
        layout: 'border',
        //autoHeight: true,
        //height: 600,
        renderTo: Ext.getBody(),
        items: [{
            xtype: 'ext:ux:schedule-panel',
            c_options: schedule_options
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
                title: 'Information',
                //region: 'north',
                frame: true,
                border: false,
                padding: 4,
                tbar: [ {text: 'Client', iconCls: 'icon-info', handler: function() {}},
                        {text: 'Search', iconCls: 'icon-info', handler: function() {}},
                        {text: 'Add new',iconCls: 'icon-plus', handler: function() {}} ],
                items: [
                client_form,
                {
                    frame: false,
                    border: false,
                    height: 60,
                    flex: 1,
                    margins: '1 0 0 0',
                    autoScroll: true,
                    items: {
                        xtype: 'ext:ux:user-courses',
                        store: course_store,
                        del_course_url: URLS.del_user_course
                    }
                }]
            },{
                xtype: 'ext:ux:course-panel',
                dataUrl: URLS.get_course_tree
            }]
        }]
    });

    var conn = new Ext.data.Connection();
    conn.request({
        url: '/ajax/rfid/',
        method: 'POST',
        params: {},
        success: function(response) {
            var json = Ext.util.JSON.decode(response.responseText);
            var form = client_form.getForm().setValues(json);
            course_store.load({params: {rfid_code: json.rfid_code}});
        },
        failure: function() {
            alert('RFID reading failed');
        }
    });


});
