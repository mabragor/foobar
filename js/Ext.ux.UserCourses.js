Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    // set store in descendant code
    title: 'Courses',
    emptyText: 'No images to display',
    frame: true,
    border: false,
    flex: 1,
    loadingText: 'loading',
    columns: [{
        header: 'Title',
        width: .5,
        dataIndex: 'title'
    },{
        header: 'Count',
        dataIndex: 'count'
    }]
});

Ext.reg('ext:ux:user-courses', Ext.ux.UserCourses);