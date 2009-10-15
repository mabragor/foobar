Ext.onReady(function() {
    Ext.QuickTips.init();

    // This form shows information about current client. Manager may check
    // client's data, add new courses to client account, take subcharge
    // from him.
    var client_form = new Ext.form.FormPanel({
        standardSubmit: true,
        labelWidth: 100,
        frame: false,
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
	url: URLS.get_user_courses,
	storeId: 'UserCourses',
	autoDestroy: true, // destroy store when the component the store is bound to is destroyed

	root: 'courses', // get data from this key
	fields: ['title',
		 {name: 'reg_date', type: 'date'},
		 {name: 'exp_date', type: 'date'},
		 'count'
		]
    });
    course_store.load();

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
                region: 'north',
                frame: true,
                border: false,
                padding: 4,
                tbar: [ {text: 'Client', iconCls: 'icon-info', handler: function() {}},
                        {text: 'Search', iconCls: 'icon-info', handler: function() {}},
                        {text: 'Add new',iconCls: 'icon-plus', handler: function() {}} ],
                items: client_form
            },{
                xtype: 'ext:ux:user-courses',
		store: course_store,
            },{
                xtype: 'ext:ux:course-panel',
		dataUrl: URLS.get_course_tree,
            }]
        }]
    });

    var conn = new Ext.data.Connection();
    conn.request({
        url: '/ajax/rfid/',
        method: 'POST',
        params: {},
        success: function(response) {
            json = Ext.util.JSON.decode(response.responseText);
            var form = client_form.getForm().setValues(json);
        },
        failure: function() {
            alert('RFID reading failed');
        }
    });


});
