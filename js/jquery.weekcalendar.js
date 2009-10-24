/*
 * jQuery.weekCalendar v1.2.1
 * http://www.redredred.com.au/
 *
 * Requires:
 * - jquery.weekcalendar.css
 * - jquery 1.3.x
 * - jquery-ui 1.7.x (widget, drag, drop, resize)
 *
 * Copyright (c) 2009 Rob Monie
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *   
 *   If you're after a monthly calendar plugin, check out http://arshaw.com/fullcalendar/
 */

(function($) {
    $.fn.sort = function() {
            return this.pushStack( $.makeArray( [].sort.apply( this, arguments ) ) );

    };
    $.widget("ui.weekCalendar", {
        
        /***********************
         * Initialise calendar *
         ***********************/
        _init : function() {
            var self = this;
            self._computeOptions();
            self._setupEventDelegation();
            self._renderCalendar();
            self._loadCalEvents();
            self._resizeCalendar();
            //setTimeout(function() {
                //self._scrollToHour(self.options.date.getHours());
            //}, 500);
            
            $(window).unbind("resize.weekcalendar");
            $(window).bind("resize.weekcalendar", function(){
                self._resizeCalendar();
            });
            
        }, 

        _filter: {},
        /********************
         * public functions *
         ********************/
        /*
         * Refresh the events for the currently displayed week.
         */
        refresh : function() {
            this._clearCalendar();
            this._loadCalEvents(this.element.data("startDate")); //reload with existing week
        },
    
        /*
         * Clear all events currently loaded into the calendar
         */
        clear : function() {
            this._clearCalendar();  
        },
        
        /*
         * Go to this week
         */
        today : function() {
            this.options.firstDayOfWeek = 1;
            this._clearCalendar();
            this._loadCalEvents(new Date()); 
        },

        prevDay: function(){
            this.options.firstDayOfWeek = (this.options.firstDayOfWeek-1) % 7;
            this._clearCalendar();
            var newDate = new Date(this.element.data("startDate").getTime() - (MILLIS_IN_WEEK / 7));
            this._loadCalEvents(newDate);
        },

        nextDay: function(){
            this.options.firstDayOfWeek = (this.options.firstDayOfWeek+1) % 7;
            this._clearCalendar();
            var newDate = new Date(this.element.data("startDate").getTime() + (MILLIS_IN_WEEK / 7));
            this._loadCalEvents(newDate);
        },

        /*
         * Go to the previous week relative to the currently displayed week
         */
        prevWeek : function() {
            //minus more than 1 day to be sure we're in previous week - account for daylight savings or other anomolies
            var newDate = new Date(this.element.data("startDate").getTime() - (MILLIS_IN_WEEK / 6));
            this._clearCalendar();   
            this._loadCalEvents(newDate);
        },
    
        /*
         * Go to the next week relative to the currently displayed week
         */
        nextWeek : function() {
            //add 8 days to be sure of being in prev week - allows for daylight savings or other anomolies
            var newDate = new Date(this.element.data("startDate").getTime() + MILLIS_IN_WEEK + (MILLIS_IN_WEEK / 7));
            this._clearCalendar();
            this._loadCalEvents(newDate); 
        },

        filterByParam: function(param){
            this.updateFilter(param);
            this._clearCalendar();
            this._loadCalEvents(this.element.data("startDate"));
        },

        /*
         * Reload the calendar to whatever week the date passed in falls on.
         */
        gotoWeek : function(date) {
            this._clearCalendar();
            this._loadCalEvents(date);
        },

        updateFilter: function(param){
            this._filter = $.extend(this.filter, param);
        },

        /*
         * Remove an event based on it's id
         */
        removeEvent : function(eventId) {
            var $self = this;
            this.element.find(".cal-event").each(function(){
                if($(this).data("calEvent").id === eventId) {
                    $(this).fadeOut(function(){
                        var $weekDay = $(this).parent();
                        $(this).remove();
                        $self._adjustOverlappingEvents($weekDay);
                    });
                    return false;
                }
            });
        },
        
        /*
         * Removes any events that have been added but not yet saved (have no id). 
         * This is useful to call after adding a freshly saved new event.
         */
        removeUnsavedEvents : function() {
            this.element.find(".new-cal-event").fadeOut(function(){
                $(this).remove();
            });
        },
        
        /*
         * update an event in the calendar. If the event exists it refreshes 
         * it's rendering. If it's a new event that does not exist in the calendar
         * it will be added.
         */
        updateEvent : function (calEvent) {
            this._updateEventInCalendar(calEvent);
        },
        
        /*
         * Returns an array of timeslot start and end times based on 
         * the configured grid of the calendar. Returns in both date and
         * formatted time based on the 'timeFormat' config option.
         */
        getTimeslotTimes : function(date) {
            var options = this.options;
            var firstHourDisplayed = options.businessHours.limitDisplay ? options.businessHours.start : 0;
            var startDate = new Date(date.getFullYear(), date.getMonth(), date.getDate(), firstHourDisplayed);
            
            var times = []
            var startMillis = startDate.getTime();
            for(var i=0; i < options.timeslotsPerDay; i++) {
                var endMillis = startMillis + options.millisPerTimeslot;
                times[i] = {
                    start: new Date(startMillis),
                    //startValue: this._formatDate(new Date(startMillis), 'Y-m-d H:i:s'),
                    startValue: (new Date(startMillis)).format('Y-m-d H:i:s'),
                    //startFormatted: this._formatDate(new Date(startMillis), options.timeFormat),
                    startFormatted: (new Date(startMillis)).format(options.timeFormat),
                    end: new Date(endMillis),
                    //endFormatted: this._formatDate(new Date(endMillis), options.timeFormat)
                    endFormatted: (new Date(endMillis)).format(options.timeFormat)
                 };
                startMillis = endMillis;
            }
            return times;
        }, 
        
        formatDate : function(date, format) {
           if(format) {
                //return this._formatDate(date, format);
                return date.format(format);
           } else {
                //return this._formatDate(date, this.options.dateFormat);
                return date.format(this.options.dateFormat);
           }
        },
        
        formatTime : function(date, format) {
           if(format) {
                //return this._formatDate(date, format);
                return date.format(format);
           } else {
                //return this._formatDate(date, this.options.timeFormat);
                return date.format(this.options.timeFormat);
           }
        },
        
        getData : function(key) {
           return this._getData(key); 
        },
        
        /*********************
         * private functions *
         *********************/
        // compute dynamic options based on other config values    
        _computeOptions : function() {
            
            var options = this.options;
            
            if(options.businessHours.limitDisplay) {
                options.timeslotsPerDay = options.timeslotsPerHour * (options.businessHours.end - options.businessHours.start);
                options.millisToDisplay = (options.businessHours.end - options.businessHours.start) * 60 * 60 * 1000;
                options.millisPerTimeslot = options.millisToDisplay / options.timeslotsPerDay;
            } else {
                options.timeslotsPerDay = options.timeslotsPerHour * 24;
                options.millisToDisplay = MILLIS_IN_DAY;
                options.millisPerTimeslot = MILLIS_IN_DAY / options.timeslotsPerDay;
            }  
        },
        
        /*
         * Resize the calendar scrollable height based on the provided function in options.
         */
        _resizeCalendar : function () {
            var options = this.options;
            if(options && $.isFunction(options.height)) {
                var calendarHeight = options.height(this.element);
                var headerHeight = this.element.find(".week-calendar-header").outerHeight();
                var navHeight = this.element.find(".calendar-nav").outerHeight();
                //this.element.find(".calendar-scrollable-grid").height(calendarHeight - navHeight - headerHeight);
                this.element.find(".calendar-scrollable-grid").css('height', '88%');
            }
        },
        
        /*
         * configure calendar interaction events that are able to use event 
         * delegation for greater efficiency 
         */
        _setupEventDelegation: function() {
            var self = this;
            var options = this.options;
            this.element.mouseover(function(event){
                var $target = $(event.target);
                
                if(self._isDraggingOrResizing($target)) {
                    return;
                }

                if($target.parent().hasClass("cal-event") ) {
                    options.eventMouseover($target.data("calEvent"), $target, event);
                } 
            }).mouseout(function(event){
                var $target = $(event.target);
                if(self._isDraggingOrResizing($target)) {
                    return;
                }
                if($target.parent().hasClass("cal-event")) {
                    if($target.data("sizing")) return;
                    options.eventMouseout($target.data("calEvent"), $target, event);
                   
                } 
            });
        }, 
        
        /*
         * check if a ui draggable or resizable is currently being dragged or resized
         */
        _isDraggingOrResizing : function ($target) {
            return $target.hasClass("ui-draggable-dragging") || $target.hasClass("ui-resizable-resizing");
        },
        
        /*
         * Render the main calendar layout
         */
        _renderCalendar : function() {
            
            var $calendarContainer, calendarHeaderHtml, calendarBodyHtml, $weekDayColumns;
            var self = this;
            var options = this.options;
            
            $calendarContainer = $("<div class=\"week-calendar\">").appendTo(self.element);
            
            //render calendar header
            calendarHeaderHtml = "<table class=\"week-calendar-header ui-widget-content\"><tbody><tr><td class=\"time-column-header\"></td>";
            for(var i=1 ; i<=7; i++) {
                calendarHeaderHtml += "<td class=\"day-column-header day-" + i + "\"></td>";
            }
            calendarHeaderHtml += "<td class=\"scrollbar-shim\"></td></tr></tbody></table>";
                        
            //render calendar body
            calendarBodyHtml = "<div class=\"calendar-scrollable-grid\">\
                <table class=\"week-calendar-time-slots\">\
                <tbody>\
                <tr>\
                <td class=\"grid-timeslot-header\"></td>\
                <td colspan=\"7\">\
                <div class=\"time-slot-wrapper\">\
                <div class=\"time-slots\">";
            
            var start = options.businessHours.limitDisplay ? options.businessHours.start : 0;
            var end = options.businessHours.limitDisplay ? options.businessHours.end : 24;    
                
            for(var i = start ; i < end; i++) {
                for(var j=0;j<options.timeslotsPerHour - 1; j++) {
                    calendarBodyHtml += "<div class=\"time-slot\"></div>";
                }   
                calendarBodyHtml += "<div class=\"time-slot hour-end\"></div>"; 
            }
            
            calendarBodyHtml += "</div></div></td></tr><tr><td class=\"grid-timeslot-header\">";
        
            for(var i = start ; i < end; i++) {
    
                var bhClass = (options.businessHours.start <= i && options.businessHours.end > i) ? "business-hours" : "";                 
                calendarBodyHtml += "<div class=\"hour-header " + bhClass + " ui-widget-content\">"
                if(options.use24Hour) {
                   calendarBodyHtml += "<div class=\"time-header-cell\">" + self._24HourForIndex(i) + "</div>";
                } else {
                   calendarBodyHtml += "<div class=\"time-header-cell\">" + self._hourForIndex(i) + "<span class=\"am-pm\">" + self._amOrPm(i) + "</span></div>";
                }
                calendarBodyHtml += "</div>";
            }
            
            calendarBodyHtml += "</td>";
            
            for(var i=1 ; i<=7; i++) {
                calendarBodyHtml += "<td class=\"day-column day-" + i + "\"><div class=\"day-column-inner\"></div></td>"
            }
            
            calendarBodyHtml += "</tr></tbody></table></div>";
            
            //append all calendar parts to container            
            $(calendarHeaderHtml + calendarBodyHtml).appendTo($calendarContainer);
            
            $weekDayColumns = $calendarContainer.find(".day-column-inner");
            $weekDayColumns.each(function(i, val) {
                $(this).height(options.timeslotHeight * options.timeslotsPerDay); 
                if(!options.readonly) {
                   self._addDroppableToWeekDay($(this));
                }
            });
            
            $calendarContainer.find(".time-slot").height(options.timeslotHeight -1); //account for border
            
            $calendarContainer.find(".time-header-cell").css({
                    height :  (options.timeslotHeight * options.timeslotsPerHour) - 12,
                    padding: 5
            });
       },
        
        /*
         * load calendar events for the week based on the date provided
         */
        _loadCalEvents : function(dateWithinWeek) {
            
            var date, weekStartDate, weekEndDate, $weekDayColumns;
            var self = this;
            var options = this.options;
            date = dateWithinWeek || options.date;
            weekStartDate = self._dateFirstDayOfWeek(date);
            weekEndDate = self._dateLastMilliOfWeek(date);
            
            options.calendarBeforeLoad(self.element);

            self.element.data("startDate", weekStartDate);
            self.element.data("endDate", weekEndDate);
            
            $weekDayColumns = self.element.find(".day-column-inner");
            
            self._updateDayColumnHeader($weekDayColumns);
            
            //load events by chosen means        
            if (typeof options.data == 'string') {
                if (options.loading) options.loading(true);
                var jsonOptions = {};
                jsonOptions[options.startParam || 'start'] = Math.round(weekStartDate.getTime() / 1000);
                jsonOptions[options.endParam || 'end'] = Math.round(weekEndDate.getTime() / 1000);
                $.getJSON(options.data, jsonOptions, function(data) {
                    self._renderEvents(data, $weekDayColumns);
                    if (options.loading) options.loading(false);
                });
            }
            else if ($.isFunction(options.data)) {
                options.data.call(this, weekStartDate, weekEndDate,
                    function(data) {
                        self._renderEvents(data, $weekDayColumns);
                    }, this._filter);
            }
            else if (options.data) {
                self._renderEvents(options.data, $weekDayColumns);
            }
            
            self._disableTextSelect($weekDayColumns);
           
            
        },
        
        /*
         * update the display of each day column header based on the calendar week
         */
        _updateDayColumnHeader : function ($weekDayColumns) {
            var self = this;
            var options = this.options;            
            var currentDay = self._cloneDate(self.element.data("startDate"));
    
            self.element.find(".week-calendar-header td.day-column-header").each(function(i, val) {
                
                    var dayName = options.useShortDayNames ? options.shortDays[currentDay.getDay()] : options.longDays[currentDay.getDay()];
                
                    //$(this).html(dayName + "<br/>" + self._formatDate(currentDay, options.dateFormat));
                    $(this).html(dayName + "<br/>" + currentDay.format(options.dateFormat));
                    if(self._isToday(currentDay)) {
                        $(this).addClass("today");
                    } else {
                        $(this).removeClass("today");
                    }
                    currentDay = self._addDays(currentDay, 1);
                
            });
            
            currentDay = self._dateFirstDayOfWeek(self._cloneDate(self.element.data("startDate")));
            
            $weekDayColumns.each(function(i, val) {
                
                $(this).data("startDate", self._cloneDate(currentDay));
                $(this).data("endDate", new Date(currentDay.getTime() + (MILLIS_IN_DAY - 1)));          
                if(self._isToday(currentDay)) {
                    $(this).parent().addClass("today");
                } else {
                    $(this).parent().removeClass("today");
                }
                
                currentDay = self._addDays(currentDay, 1);
            });
            
        },
        
        /*
         * Render the events into the calendar
         */
        _renderEvents : function (events, $weekDayColumns) {
            var self = this;
            var options = this.options;
            var eventsToRender;

            if($.isArray(events)) {
                eventsToRender = self._cleanEvents(events);
            } else if(events.events) {
                 eventsToRender = self._cleanEvents(events.events);
            }
            if(events.options) {
                
                var updateLayout = false;
                //update options
                $.each(events.options, function(key, value){
                    if(value !== options[key]) {
                        options[key] = value;
                        updateLayout = true;
                    }
                });
                
                self._computeOptions();
                
                if(updateLayout) {
                    self.element.empty();
                    self._renderCalendar();
                    $weekDayColumns = self.element.find(".week-calendar-time-slots .day-column-inner");
                    self._updateDayColumnHeader($weekDayColumns);
                    self._resizeCalendar();
                }
                
            }
            
             
            $.each(eventsToRender, function(i, calEvent){
                
                var $weekDay = self._findWeekDayForEvent(calEvent, $weekDayColumns);
                
                if($weekDay) {
                    self._renderEvent(calEvent, $weekDay);
                }
            });
            
            $weekDayColumns.each(function(){
                self._adjustOverlappingEvents($(this));
            });
            //self._addDeleteEvent();
            options.calendarAfterLoad(self.element);
            
            if(!eventsToRender.length) {
                options.noEvents();
            }
            
        },
        
        /*
         * Render a specific event into the day provided. Assumes correct 
         * day for calEvent date
         */
        _renderEvent: function (calEvent, $weekDay) {
            var self = this;
            var options = this.options;
            if(calEvent[options.startParam].getTime() > calEvent[options.endParam].getTime()) {
                return; // can't render a negative height
            }

            var eventClass, eventHtml, $calEvent, $modifiedEvent;
            
            eventClass = calEvent.id ? "cal-event" : "cal-event new-cal-event";
            eventHtml = "<div class=\"" + eventClass + " ui-corner-all\">\
                <div class=\"time ui-corner-all\"></div>\
                <div class=\"title\"></div>";
            if(calEvent[options.startParam].getTime() > (new Date()).getTime()){
                eventHtml += "<div class=\"delete-event\">&nbsp;</div>";
            }
            eventHtml += "</div>";
                
            $calEvent = $(eventHtml);
            $modifiedEvent = options.eventRender.call(self, calEvent, $calEvent);
            $calEvent = $modifiedEvent ? $modifiedEvent.appendTo($weekDay) : $calEvent.appendTo($weekDay);
            $calEvent.css({lineHeight: (options.timeslotHeight - 2) + "px", fontSize: (options.timeslotHeight / 2) + "px"});
            
            self._refreshEventDetails(calEvent, $calEvent);
            self._positionEvent($weekDay, $calEvent);
            $calEvent.show();
            $calEvent.find('div.delete-event').bind("mousedown", function(){
                var calEvent = $(this).parent().data("calEvent");
                self.options.eventDelete.call(self, calEvent);
            });
            $calEvent.mouseenter(function(event){
                $(this).find(".delete-event").fadeIn('fast');
            }).mouseleave(function(event){
                $(this).find(".delete-event").fadeOut('fast');
            });
            if(!options.readonly && options.resizable(calEvent, $calEvent)) {
                self._addResizableToCalEvent(calEvent, $calEvent, $weekDay)
            }
            if(!options.readonly && options.draggable(calEvent, $calEvent)) {
                self._addDraggableToCalEvent(calEvent, $calEvent);
            } 
            options.eventAfterRender.call(self, calEvent, $calEvent);
            
            return $calEvent;
            
        },

        /*
         * If overlapping is allowed, check for overlapping events and format 
         * for greater readability
         */
        _adjustOverlappingEvents : function($weekDay) {
            var self = this;
            
            if(self.options.allowCalEventOverlap) {

                var groups = self._groupOverlappingEventElements($weekDay);

                $.each(groups, function(){
                    var groupAmount = this.length;
                    var curGroup = this;
                    // do we want events to be displayed as overlapping 
                    if (self.options.overlapEventsSeparate){
                        var newWidth = 100/groupAmount;
                        var newLeftAdd = newWidth;
                    } else {
                        // TODO what happens when the group has more than 10 elements
                        var newWidth = (100 - (groupAmount*10));
                        var newLeftAdd = (100 - newWidth) / (groupAmount-1);
                    }
                    $.each(this, function(i){
                        $(this).css({lineHeight: '10px'}).find('div').css({color: $(this).css('backgroundColor')});
                        var newLeft = (i * newLeftAdd); 
                        // bring mouseovered event to the front
                        /*
                        $(this).css({'font-size': '10px',
                                     'line-height': '15px'});*/
                        //------------------------------------
                        if(!self.options.overlapEventsSeparate){
                            $(this).bind("mouseover.z-index",function(){
                                 var $elem = $(this);
                                 $.each(curGroup, function() {
					                $(this).css({"z-index":  "1"});
					            });
					            $elem.css({"z-index": "3"});
                            });
                        }
                        $(this).css({width: newWidth+"%", left: newLeft+"%", right: 0});
                    });
                });
            }
        },
        
       
        /*
         * Find groups of overlapping events
         */
        _groupOverlappingEventElements : function($weekDay) {
            var self = this;
            var options = self.options;
            var $events = $weekDay.find(".cal-event");

            var sortedEvents = $events.sort(function(a, b){
                return $(a).data("calEvent")[options.startParam].getTime() - $(b).data("calEvent")[options.startParam].getTime();
            });
            
            var $lastEvent;
            var groups = [];
            var currentGroup = [];
            var $curEvent;
            var currentGroupStartTime = 0;
            var currentGroupEndTime = 0;
            var lastGroupEndTime = 0;
            $.each(sortedEvents, function(){
                
                $curEvent = $(this);
                currentGroupStartTime = $curEvent.data("calEvent")[options.startParam].getTime();
                currentGroupEndTime = $curEvent.data("calEvent")[options.endParam].getTime();
                $curEvent.css({width: "100%", left: "0%", right: "", "z-index": "1", lineHeight: (options.timeslotHeight - 2) + "px"}).find('div').css('color', '');
                $curEvent.unbind("mouseover.z-index");
                // if current start time is lower than current endtime time than either this event is earlier than the group, or already within the group   
                if ($curEvent.data("calEvent")[options.startParam].getTime() < lastGroupEndTime) {
                    return;
                }
                // loop through all current weekday events to check if they belong to the same group
                $.each(sortedEvents, function() {
                    // check for same element and possibility to even be in the same group  note: somehow ($curEvent == $(this) doens't work 
                    if ($curEvent.data("calEvent").id == $(this).data("calEvent").id || 
                        currentGroupStartTime > $(this).data("calEvent")[options.startParam].getTime()+1 ||
                        currentGroupEndTime < $(this).data("calEvent")[options.startParam].getTime()+1) {
                        return;
                    }
                    //set new endtime of the group
                    if ($(this).data("calEvent").end.getTime() > currentGroupEndTime) {
                        currentGroupEndTime = $(this).data("calEvent").end.getTime();
                    }
                    // ain't we adding the same element
                    if ($.inArray($(this), currentGroup) == -1) {
                        currentGroup.push($(this));
                    }
                    // ain't we adding the same element
                    if ($.inArray($curEvent, currentGroup) == -1) {
                        currentGroup.push($curEvent);
                    }
                });
                if(currentGroup.length) {
                    currentGroup.sort(function(a,b){
                        if ($(a).data("calEvent")[options.startParam].getTime() > $(b).data("calEvent")[options.startParam].getTime()) {
                            return 1;
                        } else if ($(a).data("calEvent")[options.startParam].getTime() < $(b).data("calEvent")[options.startParam].getTime()) {
                            return -1;
                        } else {
                            return ($(a).data("calEvent")[options.endParam].getTime() - $(a).data("calEvent")[options.startParam].getTime())
                                         - ($(b).data("calEvent")[options.endParam].getTime() - $(b).data("calEvent")[options.startParam].getTime());
                        }
                    });
                    groups.push(currentGroup);
                    currentGroup = [];
                    lastGroupEndTime = currentGroupEndTime;
                } 
            
            });
            
            return groups;
            
        },
        /*
         * Check if two groups containt the same events. It assumes the groups are sorted NOTE: might be obsolete
         */
        _compareGroups: function(thisGroup, thatGroup){
            if (thisGroup.length != thatGroup.length) {
                return false;
            }
            
            for (var i = 0; i < thisGroup.length; i++) {
                if (thisGroup[i].data("calEvent").id != thatGroup[i].data("calEvent").id) {
                    return false;
                }
            }
            
            return true;
        },  


        
        /*
         * find the weekday in the current calendar that the calEvent falls within
         */
        _findWeekDayForEvent : function(calEvent, $weekDayColumns) {
            var options = this.options;
            var $weekDay;
            $weekDayColumns.each(function(){
                if($(this).data("startDate").getTime() <= calEvent[options.startParam].getTime() && $(this).data("endDate").getTime() >= calEvent[options.endParam].getTime()) {
                    $weekDay = $(this);
                    return false;
                } 
            }); 
            return $weekDay;
        },
        
        /*
         * update the events rendering in the calendar. Add if does not yet exist.
         */
        _updateEventInCalendar : function (calEvent) {
            var self = this;
            var options = this.options;
            self._cleanEvent(calEvent);
            
            if(calEvent.id) {
                self.element.find(".cal-event").each(function(){
                    if($(this).data("calEvent").id === calEvent.id || $(this).hasClass("new-cal-event")) {
                        $(this).remove();
                        return false;
                    }
                });
            }
            
            var $weekDay = self._findWeekDayForEvent(calEvent, self.element.find(".week-calendar-time-slots .day-column-inner"));
            if($weekDay) {
                self._renderEvent(calEvent, $weekDay);
                self._adjustOverlappingEvents($weekDay);
            }
        },
        
        /*
         * Position the event element within the weekday based on it's start / end dates.
         */
        _positionEvent : function($weekDay, $calEvent) {
            var options = this.options;
            var calEvent = $calEvent.data("calEvent");
            var pxPerMillis = $weekDay.height() / options.millisToDisplay;
            var firstHourDisplayed = options.businessHours.limitDisplay ? options.businessHours.start : 0;
            var startMillis = calEvent[options.startParam].getTime() - new Date(calEvent[options.startParam].getFullYear(), calEvent[options.startParam].getMonth(), calEvent[options.startParam].getDate(), firstHourDisplayed).getTime();
            var eventMillis = calEvent[options.endParam].getTime() - calEvent[options.startParam].getTime();
            var pxTop = pxPerMillis * startMillis;
            var pxHeight = pxPerMillis * eventMillis;
            $calEvent.css({top: pxTop, height: pxHeight});
        },
    
        /*
         * Determine the actual start and end times of a calevent based on it's 
         * relative position within the weekday column and the starting hour of the
         * displayed calendar.
         */
        _getEventDurationFromPositionedEventElement : function($weekDay, $calEvent, top) {
             var options = this.options;
             var startOffsetMillis = options.businessHours.limitDisplay ? options.businessHours.start * 60 *60 * 1000 : 0;
             var start = new Date($weekDay.data("startDate").getTime() + startOffsetMillis + Math.round(top / options.timeslotHeight) * options.millisPerTimeslot);
             var end = new Date(start.getTime() + ($calEvent.height() / options.timeslotHeight) * options.millisPerTimeslot);
             return {start: start, end: end};
        },
        
        /*
         * If the calendar does not allow event overlap, adjust the start or end date if necessary to 
         * avoid overlapping of events. Typically, shortens the resized / dropped event to it's max possible
         * duration  based on the overlap. If no satisfactory adjustment can be made, the event is reverted to
         * it's original location.
         */
        _adjustForEventCollisions : function($weekDay, $calEvent, newCalEvent, oldCalEvent, maintainEventDuration) {
            var options = this.options;
            
            if(options.allowCalEventOverlap) {
                return;
            }
            var adjustedStart, adjustedEnd;
            var self = this;
    
            $weekDay.find(".cal-event").not($calEvent).each(function(){
                var currentCalEvent = $(this).data("calEvent");
                
                //has been dropped onto existing event overlapping the end time
                if(newCalEvent[options.startParam].getTime() < currentCalEvent[options.endParam].getTime()
                    && newCalEvent[options.endParam].getTime() >= currentCalEvent[options.endParam].getTime()) {
                  
                  adjustedStart = currentCalEvent[options.endParam];
                }
                
                
                //has been dropped onto existing event overlapping the start time
                if(newCalEvent.end.getTime() > currentCalEvent[options.startParam].getTime()
                    && newCalEvent[options.startParam].getTime() <= currentCalEvent[options.startParam].getTime()) {
                  
                  adjustedEnd = currentCalEvent[options.startParam];
                }
                //has been dropped inside existing event with same or larger duration
                if(newCalEvent.end.getTime() <= currentCalEvent.end.getTime() 
                    && newCalEvent[options.startParam].getTime() >= currentCalEvent[options.startParam].getTime()) {
                       
                    adjustedStart = oldCalEvent[options.startParam];
                    adjustedEnd = oldCalEvent.end;
                    return false;
                }
                
            });
            
            
            newCalEvent[options.startParam] = adjustedStart || newCalEvent[options.startParam];
            
            if(adjustedStart && maintainEventDuration) {
                newCalEvent.end = new Date(adjustedStart.getTime() + (oldCalEvent.end.getTime() - oldCalEvent[options.startParam].getTime()));
                self._adjustForEventCollisions($weekDay, $calEvent, newCalEvent, oldCalEvent);
            } else {
                newCalEvent.end = adjustedEnd || newCalEvent.end;
            }
            
            
            
            //reset if new cal event has been forced to zero size
            if(newCalEvent[options.startParam].getTime() >= newCalEvent.end.getTime()) {
                newCalEvent[options.startParam] = oldCalEvent[options.startParam];
                newCalEvent.end = oldCalEvent.end;
            }
            
            $calEvent.data("calEvent", newCalEvent);
        },
        
        /*
         * Add draggable capabilities to an event
         */
        _addDraggableToCalEvent : function(calEvent, $calEvent) {
            var self = this;
            var options = this.options;
            var $weekDay = self._findWeekDayForEvent(calEvent, self.element.find(".week-calendar-time-slots .day-column-inner"));
            $calEvent.draggable({
                handle : ".time",
                //containment: ".calendar-scrollable-grid",
                containment: ".week-calendar-time-slots",
                //revert: 'valid',
                opacity: 0.5,
                helper: 'clone',
                grid : [$calEvent.outerWidth() + 1, options.timeslotHeight ],
                start : function(event, ui) {
                    var $calEvent = ui.draggable;
                    options.eventDrag(calEvent, $calEvent);
                }
            });
            
        },
        
        /*
         * Add droppable capabilites to weekdays to allow dropping of calEvents only
         */
        _addDroppableToWeekDay : function($weekDay) {
            var self = this;
            var options = this.options;
            $weekDay.droppable({
                accept: ".cal-event",
                drop: function(event, ui) {
                    var $calEvent = ui.draggable;
                    var top = Math.round(parseInt(ui.position.top));
                    var eventDuration = self._getEventDurationFromPositionedEventElement($weekDay, $calEvent, top);
                    var calEvent = $calEvent.data("calEvent");
                    var newCalEvent = $.extend(true, {start: eventDuration.start, end: eventDuration.end}, calEvent);
                    //self._adjustForEventCollisions($weekDay, $calEvent, newCalEvent, calEvent, true);
                    //var $weekDayColumns = self.element.find(".day-column-inner");
                    //var $newEvent = self._renderEvent(newCalEvent, self._findWeekDayForEvent(newCalEvent, $weekDayColumns));
                    //$calEvent.hide();

                    function move_event(){
                        self._adjustForEventCollisions($weekDay, $calEvent, newCalEvent, calEvent, true);
                        var $weekDayColumns = self.element.find(".day-column-inner");
                        var $newEvent = self._renderEvent(newCalEvent, self._findWeekDayForEvent(newCalEvent, $weekDayColumns));
                        //$calEvent.hide();

                        //$calEvent.data("preventClick", true);
                        setTimeout(function(){
                            var $weekDayOld = self._findWeekDayForEvent($calEvent.data("calEvent"), self.element.find(".week-calendar-time-slots .day-column-inner"));
                            $calEvent.remove();
                            if ($weekDayOld.data("startDate") != $weekDay.data("startDate")) {
                                self._adjustOverlappingEvents($weekDayOld);
                            }
                            self._adjustOverlappingEvents($weekDay);
                        }, 500);
                    }
                    //trigger drop callback
                    options.eventDrop.call(self, newCalEvent, move_event, function(){$calEvent.show()});
                    $calEvent.data("preventClick", true);
                    /*
                        setTimeout(function(){

                            var $weekDayOld = self._findWeekDayForEvent($calEvent.data("calEvent"), self.element.find(".week-calendar-time-slots .day-column-inner"));
                            $calEvent.remove();
                            if ($weekDayOld.data("startDate") != $weekDay.data("startDate")) {
                                self._adjustOverlappingEvents($weekDayOld);
                            }
                            self._adjustOverlappingEvents($weekDay);
                        }, 500);
                       */
                }
            });
        },
        
        /*
         * Add resizable capabilities to a calEvent
         */
        _addResizableToCalEvent : function(calEvent, $calEvent, $weekDay) {
            var self = this;
            var options = this.options;
            $calEvent.resizable({
                grid: options.timeslotHeight,
                containment : $weekDay,
                handles: "s",
                minHeight: options.timeslotHeight,
                stop :function(event, ui){
                    var $calEvent = ui.element;  
                    var newEnd = new Date($calEvent.data("calEvent")[options.startParam].getTime() + ($calEvent.height() / options.timeslotHeight) * options.millisPerTimeslot);
                    var newCalEvent = $.extend(true, {start: calEvent[options.startParam], end: newEnd}, calEvent);
                    self._adjustForEventCollisions($weekDay, $calEvent, newCalEvent, calEvent);
                    
                    self._refreshEventDetails(newCalEvent, $calEvent);
                    self._positionEvent($weekDay, $calEvent);
                    
                    //trigger resize callback
                    options.eventResize(newCalEvent, calEvent, $calEvent);
                    $calEvent.data("preventClick", true);
                    setTimeout(function(){
                        $calEvent.removeData("preventClick");
                    }, 500);
                }
            });
        },
        
        /*
         * Refresh the displayed details of a calEvent in the calendar
         */
        _refreshEventDetails : function(calEvent, $calEvent) {
            var self = this;
            var options = this.options;            $calEvent.find(".time").text(calEvent[options.startParam].format(options.timeFormat) + options.timeSeparator + calEvent[options.endParam].format(options.timeFormat));
            $calEvent.find(".title").text(calEvent.title);
            $calEvent.data("calEvent", calEvent);
        },
        
        /*
         * Clear all cal events from the calendar
         */
        _clearCalendar : function() {
            this.element.find(".day-column-inner div").remove();
        },
        
        /*
         * Scroll the calendar to a specific hour
         */
        _scrollToHour : function(hour) {
            var self = this;
            var options = this.options;
            var $scrollable = this.element.find(".calendar-scrollable-grid");
            var slot = hour;
            if(self.options.businessHours.limitDisplay) {
               if(hour < self.options.businessHours.start) {
                    slot = 0; 
               } else if(hour > self.options.businessHours.end) {
                    slot = self.options.businessHours.end - self.options.businessHours.start - 1;
               }
            }

            var $target = this.element.find(".grid-timeslot-header .hour-header:eq(" + slot + ")");
            
            $scrollable.animate({scrollTop: 0}, 0, function(){
                var targetOffset = $target.offset().top;
                var scroll = targetOffset - $scrollable.offset().top - $target.outerHeight();
                $scrollable.animate({scrollTop: scroll}, options.scrollToHourMillis);
            });
        },
    
        /*
         * find the hour (12 hour day) for a given hour index
         */
        _hourForIndex : function(index) {
            if(index === 0 ) { //midnight
                return 12; 
            } else if(index < 13) { //am
                return index;
            } else { //pm
                return index - 12;
            }
        },
        
        _24HourForIndex : function(index) {
            if(index === 0 ) { //midnight
                return "00:00"; 
            } else if(index < 10) { 
                return "0"+index+":00";
            } else { 
                return index+":00";
            }
        },
        
        _amOrPm : function (hourOfDay) {
            return hourOfDay < 12 ? "AM" : "PM";
        },
        
        _isToday : function(date) {
            var clonedDate = this._cloneDate(date);
            this._clearTime(clonedDate);
            var today = new Date();
            this._clearTime(today);
            return today.getTime() === clonedDate.getTime();
        },
    
        /*
         * Clean events to ensure correct format
         */
        _cleanEvents : function(events) {
            var self = this;
            $.each(events, function(i, event) {
                self._cleanEvent(event);
            });
            return events;
        },
        
        /*
         * Clean specific event
         */
        _cleanEvent : function (event) {
            var options = this.options;
            if (event.date) {
                event[options.startParam] = event.date;
            }
            event[options.startParam] = this._cleanDate(event[options.startParam]);
            event.end = this._cleanDate(event.end);
            if (!event.end) {
                event.end = this._addDays(this._cloneDate(event[options.startParam]), 1);
            }
        },
    
        /*
         * Disable text selection of the elements in different browsers
         */
        _disableTextSelect : function($elements) {
            $elements.each(function(){
                if($.browser.mozilla){//Firefox
                    $(this).css('MozUserSelect','none');
                }else if($.browser.msie){//IE
                    $(this).bind('selectstart',function(){return false;});
                }else{//Opera, etc.
                    $(this).mousedown(function(){return false;});
                }
            });
        }, 
    
       /*
        * returns the date on the first millisecond of the week
        */
        _dateFirstDayOfWeek : function(date) {
            var self = this;
            var midnightCurrentDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            var millisToSubtract = self._getAdjustedDayIndex(midnightCurrentDate) * 86400000;
            return new Date(midnightCurrentDate.getTime() - millisToSubtract);
            
        },
        
        /*
        * returns the date on the first millisecond of the last day of the week
        */
        _dateLastDayOfWeek : function(date) {
            var self = this;
            var midnightCurrentDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            var millisToAdd = (6 - self._getAdjustedDayIndex(midnightCurrentDate)) * MILLIS_IN_DAY;
            return new Date(midnightCurrentDate.getTime() + millisToAdd);
        },
        
        /*
         * gets the index of the current day adjusted based on options
         */
        _getAdjustedDayIndex : function(date) {
            
            var midnightCurrentDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
            var currentDayOfStandardWeek = midnightCurrentDate.getDay();
            var days = [0,1,2,3,4,5,6];
            this._rotate(days, this.options.firstDayOfWeek);
            return days[currentDayOfStandardWeek];
        },
        
        /*
        * returns the date on the last millisecond of the week
        */
        _dateLastMilliOfWeek : function(date) {
            var lastDayOfWeek = this._dateLastDayOfWeek(date);
            return new Date(lastDayOfWeek.getTime() + (MILLIS_IN_DAY - 1));
            
        },
        
        /*
        * Clear the time components of a date leaving the date 
        * of the first milli of day
        */
        _clearTime : function(d) {
            d.setHours(0); 
            d.setMinutes(0);
            d.setSeconds(0); 
            d.setMilliseconds(0);
            return d;
        },
        
        /*
        * add specific number of days to date
        */
        _addDays : function(d, n, keepTime) {
            d.setDate(d.getDate() + n);
            if (keepTime) {
                return d;
            }
            return this._clearTime(d);
        },
        
        /*
         * Rotate an array by specified number of places. 
         */
        _rotate : function(a /*array*/, p /* integer, positive integer rotate to the right, negative to the left... */){ 
		    for(var l = a.length, p = (Math.abs(p) >= l && (p %= l), p < 0 && (p += l), p), i, x; p; p = (Math.ceil(l / p) - 1) * p - l + (l = p)) {
		        for(i = l; i > p; x = a[--i], a[i] = a[i - p], a[i - p] = x);
            }
		    return a;
		},
        
        _cloneDate : function(d) {
            return new Date(+d);
        },
        
        /*
         * return a date for different representations
         */
        _cleanDate : function(d) {
            if (typeof d == 'string') {
                return $.weekCalendar.parseISO8601(d, true) || Date.parse(d) || new Date(parseInt(d));
            }
            if (typeof d == 'number') {
                return new Date(d);
            }
            return d;
        },

        getClickTime: function(clickY, $weekDay){
            var options = this.options;
            var top = (clickY - (clickY % options.timeslotHeight)) / options.timeslotHeight * options.timeslotHeight;
            var start = $weekDay.data("startDate").add(Date.HOUR, options.businessHours.limitDisplay ? options.businessHours.start : 0)
                    .add(Date.HOUR, Math.round(top / options.timeslotHeight)/options.timeslotsPerHour);
            return start;
        },

        copyWeek: function(){
            this.options.firstDayOfWeek = (this.options.firstDayOfWeek+1) % 7;
            this._clearCalendar();
            var newDate = new Date(this.element.data("startDate").getTime() + (MILLIS_IN_WEEK / 7));
            this._loadCalEvents(newDate);
        }
    });
   
    $.extend($.ui.weekCalendar, {
        version: '1.2.1',
        getter: ['getTimeslotTimes', 'getData', 'formatDate', 'formatTime', 'getClickTime', 'today', 'nextDay', 'prevDay', 'nextWeek', 'prevWeek', 'filterByParam', 'removeEvent', 'copyWeek'],
        defaults: {
            date: new Date(),
            timeFormat : "G:i",
            dateFormat : "M d, Y",
            use24Hour : false,
            firstDayOfWeek : 0, // 0 = Sunday, 1 = Monday, 2 = Tuesday, ... , 6 = Saturday
            useShortDayNames: false,
            timeSeparator : " - ",
            startParam : "start",
            endParam : "end",
            businessHours : {start: 8, end: 18, limitDisplay : false},
            newEventText : "New Event",
            timeslotHeight: 20,
            defaultEventLength : 2,
            timeslotsPerHour : 4,
            buttons : true,
            buttonText : {
                today : "today",
                prevWeek : "&nbsp;&lt;&lt;&lt;&nbsp;",
                nextWeek : "&nbsp;&gt;&gt;&gt;&nbsp;",
                prevDay: "&nbsp;&lt;&nbsp;",
                nextDay: "&nbsp;&gt;&nbsp;"
            },
            scrollToHourMillis : 500,
            allowCalEventOverlap : false,
            overlapEventsSeparate: false,
            readonly: false,
            draggable : function(calEvent, element) { return true;},
            resizable : function(calEvent, element) { return true;},
            eventClick : function(){},
            eventRender : function(calEvent, element) { return element;},
            eventAfterRender : function(calEvent, element) { return element;},
            eventDrag : function(calEvent, element) {},
            eventDrop : function(calEvent, element){},
            eventResize : function(calEvent, element){},
            eventNew : function(calEvent, element) {},
            eventMouseover : function(calEvent, $event) {},
            eventMouseout : function(calEvent, $event) {},
            calendarBeforeLoad : function(calendar) {},
            calendarAfterLoad : function(calendar) {},
            eventDelete: function(){},
            noEvents : function() {},
            shortMonths : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            longMonths : ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            shortDays : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            longDays : ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        }
    });
    
    var MILLIS_IN_DAY = 86400000;
    var MILLIS_IN_WEEK = MILLIS_IN_DAY * 7;
    
    $.weekCalendar = function() {
        return {
            parseISO8601 : function(s, ignoreTimezone) {
    
                // derived from http://delete.me.uk/2005/03/iso8601.html
                var regexp = "([0-9]{4})(-([0-9]{2})(-([0-9]{2})" +
                    "(T([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?" +
                    "(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?";
                var d = s.match(new RegExp(regexp));
                if (!d) return null;
                var offset = 0;
                var date = new Date(d[1], 0, 1);
                if (d[3]) { date.setMonth(d[3] - 1); }
                if (d[5]) { date.setDate(d[5]); }
                if (d[7]) { date.setHours(d[7]); }
                if (d[8]) { date.setMinutes(d[8]); }
                if (d[10]) { date.setSeconds(d[10]); }
                if (d[12]) { date.setMilliseconds(Number("0." + d[12]) * 1000); }
                if (!ignoreTimezone) {
                    if (d[14]) {
                        offset = (Number(d[16]) * 60) + Number(d[17]);
                        offset *= ((d[15] == '-') ? 1 : -1);
                    }
                    offset -= date.getTimezoneOffset();
                }
                return new Date(Number(date) + (offset * 60 * 1000));
            }
        };
    }();
    
    
})(jQuery);
