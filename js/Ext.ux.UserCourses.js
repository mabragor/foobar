Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    emptyText: 'No images to display',
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
    }]
});

Ext.reg('ext:ux:user-courses', Ext.ux.UserCourses);