Ext.ux.CoursePanel = Ext.extend(Ext.tree.TreePanel, {
    title: 'Courses',
    frame: true,
    border: false,
    flex: 1,
    root: {
        nodeType: 'async',
        text: 'root',
        id: 'root',
        expanded: true
    },
    margins: '5 0 0 0',
    rootVisible: false,
    lines: false,
    autoScroll: true,
    enableDrag: true,
    ddGroup:'t2schedule'
    /*,
    initComponent: function(){
        Ext.apply(this, {
            containerScroll: true,
            enableDD: false,
            root: new Ext.tree.AsyncTreeNode({
                id: 'root',
                text: 'root',
                expanded: true
            }),
            rootVisible: false
        });
        Ext.ux.CoursePanel.superclass.initComponent.call(this);
    }*/
});

Ext.reg('ext:ux:course-panel', Ext.ux.CoursePanel);