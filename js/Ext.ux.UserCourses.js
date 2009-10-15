Ext.ux.UserCourses = Ext.extend(Ext.ListView, {
    // set store in descendant code
    title: 'Courses',
    multiSelect: false,
    emptyText: 'No courses to display',

    border: false,
    flex: 1,

    columns: [
	{ header: 'Title', width: .5, dataIndex: 'title'},
	{ header: 'Registered', width: .2, dataIndex: 'reg_date', tpl: '{lastmod:date("m-d h:i a")}},
	{ header: 'Expired', width: .2, dataIndex: 'exp_date', tpl: '{lastmod:date("m-d h:i a")}},
	{ header: 'Rest', width: .1, dataIndex: 'count', align; 'right'},
    ]
});

Ext.reg('ext:ux:user-courses', Ext.ux.UserCourses);
