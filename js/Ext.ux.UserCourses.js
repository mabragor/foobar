Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    emptyText: 'No courses assigned yet',
    frame: true,
    border: false,
    loadingText: 'loading',
    columns: [{
        header: 'Title',
        width: .5,
        dataIndex: 'title'
    },{
        header: 'Count',
        width: .1,
	align: 'right',
        dataIndex: 'count'
    },{
        header: 'Begins',
        width: .2,
	tpl: '{reg_date:date("M d")}',
	align: 'right',
        dataIndex: 'reg_date'
    },{
        header: 'Expires',
        width: .2,
	tpl: '{exp_date:date("M d")}',
	align: 'right',
        dataIndex: 'exp_date'
    }],
    afterRender: function(){
        Ext.ux.UserCourses.superclass.afterRender.call(this);
        new Ext.dd.DropTarget(this.ownerCt.getEl(), {
            ddGroup:'t2schedule',
            notifyDrop:function(dd, e, node) {
                var store = this.getStore();
                var r = new store.recordType(
		    {title: node.node.text, count: 8, course_id: node.node.id}
		);
                store.insert(0, r);
                return true;
            }.createDelegate(this)//notifyDrop
        });//Ext.dd.DropTarget
    }
});

Ext.reg('ext:ux:user-courses', Ext.ux.UserCourses);