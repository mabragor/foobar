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
    });

    var store = new Ext.data.JsonStore({
	url: URLS.get_active_courses,
	root: 'images',
	fields: [
            'name', 'url',
            {name:'size', type: 'float'},
            {name:'lastmod', type:'date', dateFormat:'timestamp'}
	]
    });
    store.load();

    var course_list = new Ext.ListView({
	store: store,
	multiSelect: true,
	emptyText: 'No courses to display',
	reserveScrollOffset: true,
	columns: [ { header: 'Title',    width: .5,
            dataIndex: 'title'
	},{
            header: 'Expired',
            dataIndex: 'exp_date',
            tpl: '{lastmod:date("m-d h:i a")}'
	},{
            header: 'Price',
            width: .2, 
            dataIndex: 'price',
            align: 'right'
	}]
    });

    var panel = new Ext.Viewport({
        title: Ext.getDom('page-title').innerHTML,
        id: 'main',
        layout: 'border',
        //autoHeight: true,
        //height: 600,
        renderTo: Ext.getBody(),
        items: [
	    {
		region: 'center',
		title: 'Schedule',
		items: []
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
                    //layout: 'fit',
                    frame: true,
                    border: false,
                    flex: 1,
                    items: [client_form, course_list]
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
