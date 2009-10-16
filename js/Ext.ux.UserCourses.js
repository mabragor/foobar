Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    emptyText: 'No courses',
    frame: true,
    border: false,
    loadingText: 'loading',
    columns: [{
        header: 'Title',
        width: .5,
        dataIndex: 'title'
    },{
        header: 'Count',
        dataIndex: 'count'
    },{
        header: 'RegDate',
        dataIndex: 'reg_date'
    },{
        header: 'ExtDate',
        dataIndex: 'ext_date'
    }],
    afterRender: function(){
        Ext.ux.UserCourses.superclass.afterRender.call(this);
        new Ext.dd.DropTarget(this.ownerCt.getEl(), {
            ddGroup:'t2schedule',
            notifyDrop:function(dd, e, node) {
                var store = this.getStore();
                var r = new store.recordType({title: node.node.text, count: 8, corse_id: node.node.id})
                store.insert(0, r);
                return true;
            }.createDelegate(this)//notifyDrop
        });//Ext.dd.DropTarget
    }
});

Ext.reg('ext:ux:user-courses', Ext.ux.UserCourses);