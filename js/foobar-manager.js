Ext.BLANK_IMAGE_URL = './media/ext/resources/default/s.gif';

Ext.onReady(function() {
    Ext.QuickTips.init();

    var panel = new Ext.Viewport({
	title: Ext.getDom('page-title').innerHTML,
	id: 'main',
	layout: 'border',
        //autoHeight: true,
	//height: 600,
	renderTo: Ext.getBody(),
	items: [{
	    title: 'Schedule',
	    region: 'center',
	    layout: 'fit',
	    frame: true,
	    border: false
	}, {
	    region: 'west',
	    layout: 'fit',
	    frame: true,
	    border: false,
	    width: '30%',
	    split: true,
	    collapsible: true,
	    collapseMode: 'mini',
	    items: [{
		title: 'Information',
		region: 'north',
		layout: 'fit',
		frame: true,
		border: false,
		html: 'Put customer\'s card on reader, please.'
	    },{
		title: 'Courses',
		region: 'central',
		layout: 'fit',
		frame: true,
		border: false
	    }],
	    tbar: [{
		text: 'Client',
		iconCls: 'icon-info',
		handler: function() {}
	    },{
		text: 'Search',
		iconCls: 'icon-info',
		handler: function() {}
	    },{
		text: 'Add new',
		iconCls: 'icon-plus',
		handler: function() {}
	    }]
	}]
    });

});
