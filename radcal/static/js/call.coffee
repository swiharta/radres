$(document).ready ->
  get_calendar_height = ->
    $(window).height() - 80
  #from http://stackoverflow.com/a/7710866/416687
  Backbone.View::event_aggregator = _.extend({}, Backbone.Events)

  class EventFilter extends Backbone.Model

  class EventFilters extends Backbone.Collection
    model: EventFilter
    url: '/api/v1/eventfilter/?format=json'

  class Conference extends Backbone.Model

  class Conferences extends Backbone.Collection
    model: Conference
    url: '/api/v1/conference/?format=json'

    comparator: (model) ->
      model.get "name"

  class Subspecialty extends Backbone.Model

  class Subspecialties extends Backbone.Collection
    model: Subspecialty
    url: '/api/v1/subspecialty/?format=json'

    comparator: (model) ->
      model.get "name"

  class User extends Backbone.Model

  class Users extends Backbone.Collection
    model: User
    url: '/api/v1/user/?format=json'

    comparator: (model) ->
      model.get "last_name"

  class Shift extends Backbone.Model

  class Shifts extends Backbone.Collection
    model: Shift
    url: '/api/v1/shift/?format=json'

    comparator: (model) ->
      model.get "name"

  class ShiftEvent extends Backbone.Model
    defaults:
      shift: new Shift

  class ShiftEvents extends Backbone.Collection
    model: ShiftEvent
    url: '/api/v1/shiftevent/?format=json'

    search: (opts) ->
      result = @where(opts)
      resultCollection = new ShiftEvents(result)
      resultCollection

    filtered: (event_filter) ->
      result =
        @filter (model) ->
          if $.inArray(model.get("user"), event_filter.get("users")) >= 0
            true
          else if $.inArray(model.get("shift"), event_filter.get("shifts")) >= 0
            true
          else
            false

      resultCollection = new ShiftEvents(result)
      resultCollection

  class ConfEvent extends Backbone.Model

  class ConfEvents extends Backbone.Collection
    model: ConfEvent
    url: '/api/v1/confevent/?format=json'

    filtered: (event_filter) ->
      result =
        @filter (model) ->
          if $.inArray(model.get("conference"), event_filter.get("conferences")) >= 0
            true
          else if $.inArray(model.get("user"), event_filter.get("users")) >= 0
            true
          else if $.inArray(model.get("subspecialty"), event_filter.get("subspecialties")) >= 0
            true
          else
            false

      resultCollection = new ConfEvents(result)
      resultCollection


  class EventFiltersView extends Backbone.View
    initialize: ->
      @collection.bind 'reset', @addAll
      @collection.bind 'add', @addOne
      @collection.bind 'change', @change
      @collection.bind 'destroy', @destroy
      @eventFilterView = new EventFilterView(collection: event_filters, model: @options.event_filter)

    events:
      'click #event-filters .nav a.toggle': 'navClicked'
      'click #event-filters .filter.btn': 'btnClicked'
      'click #event-filters .add-all.btn': 'addAll'
      'click #event-filters .reset.btn': 'removeAll'

    render: =>
      @eventFilterView.render()
      nav_template = _.template $("#event_filters_nav_template").html()
      @$el.append nav_template
        'title': 'Filters'
        'view': '#event-filter'
      @$el.append _.template $("#event_filters_static_template").html()
      current_filter_uris = @options.event_filter.get('conferences').concat(@options.event_filter.get('users')).concat(@options.event_filter.get('shifts')).concat(@options.event_filter.get('subspecialties'))
      @collection.each ((event_filter) ->
        filter_uris = event_filter.get('conferences').concat(event_filter.get('users')).concat(event_filter.get('shifts')).concat(event_filter.get('subspecialties'))
        event_variables =
          'filter': event_filter.toJSON()
          'on': if not (_.difference(filter_uris, current_filter_uris)).length then 'on' else ''
        event_template = _.template $("#event_filters_template").html()
        compiled_event = event_template(event_variables)
        @$el.append compiled_event
      ), this
      true

    navClicked: (e) =>
      e.preventDefault()
      hash = e.currentTarget.hash
      $(hash).toggle()
      @$el.find('a[href='+e.currentTarget.hash+']').parent().toggleClass('active')
      @$el.find('.event-filter').toggle()

    btnClicked: (e) =>
      e.preventDefault()
      uri = e.currentTarget.pathname
      uri = if uri[0] is '/' then uri else '/'+uri # IE doesn't have the leading '/' for some reason
      if e.currentTarget.className.indexOf(' on') >= 0
        @options.event_filter.set
          'conferences': _.without(@options.event_filter.get('conferences'), @collection.get(uri).get('conferences'))
          'users': _.without(@options.event_filter.get('users'), @collection.get(uri).get('users'))
          'subspecialties': _.without(@options.event_filter.get('subspecialties'), @collection.get(uri).get('subspecialties'))
          'shifts': _.without(@options.event_filter.get('shifts'), @collection.get(uri).get('shifts'))
        #                          @$el.find('a').removeClass('on')
        @$el.find('a[href="'+uri+'"]').removeClass('on')
      else
        @$el.find('a[href="'+uri+'"]').addClass('on')
        #                          console.log @options.event_filter.get('conferences')
        #                          console.log @collection.get(uri).get('conferences')
        @options.event_filter.set
          'conferences': @collection.get(uri).get('conferences').concat(@options.event_filter.get('conferences'))
          'users': @collection.get(uri).get('users').concat(@options.event_filter.get('users'))
          'subspecialties': @collection.get(uri).get('subspecialties').concat(@options.event_filter.get('subspecialties'))
          'shifts': @collection.get(uri).get('shifts').concat(@options.event_filter.get('shifts'))
      @options.event_filter.save()
      @eventFilterView.render()
      @event_aggregator.trigger "event_filter:change"

    addAll: (e) =>
      e.preventDefault()
      @options.event_filter.set
        'conferences': conferences.pluck('resource_uri')
        'users': [] #users.pluck('resource_uri')
        'subspecialties': [] #subspecialties.pluck('resource_uri')
        'shifts': shifts.pluck('resource_uri')
      @$el.find('a').addClass('on')
      @options.event_filter.save()
      @eventFilterView.render()
      @event_aggregator.trigger "event_filter:change"

    removeAll: (e) =>
      e.preventDefault()
      @options.event_filter.set
        'conferences': []
        'users': []
        'subspecialties': []
        'shifts': []
      @$el.find('a').removeClass('on')
      @options.event_filter.save()
      @eventFilterView.render()
      @event_aggregator.trigger "event_filter:change"

  #                      addAll: =>
  #                      addOne: (event) =>
  #                      change: (event)  =>
  #                      destroy: (event) =>


  class EventFilterView extends Backbone.View
    el: $("#event-filter")

    events:
      'change .chzn-select': 'save'

    render: =>
      event_variables =
        'filter': @model.toJSON()
        'conferences': conferences.toJSON()
        'users': users.toJSON()
        'subspecialties': subspecialties.toJSON()
        'shifts': shifts.toJSON()
      event_template = _.template $("#event_filter_template").html()
      compiled_event = event_template(event_variables)
      @$el.html compiled_event
      @$el.find(".chzn-select").chosen()

    save: =>
      @model.set
        'conferences': $('#conferences').val()
        'users': $('#users').val()
        'subspecialties': $('#subspecialties').val()
        'shifts': $('#shifts').val()
      @model.save()
      @event_aggregator.trigger "event_filter:change"


  class EventsView extends Backbone.View
    initialize: ->
      @collection.bind 'reset', @addAll
      @collection.bind 'add', @addOne
      @collection.bind 'change', @change
      @collection.bind 'destroy', @destroy
      #                        @options.collection2.bind 'reset', @addAll
      @options.collection2.bind 'add', @addOne
      @options.collection2.bind 'change', @change
      @options.collection2.bind 'destroy', @destroy

      @event_aggregator.bind "event_filter:change", @addAll

      @eventView = new EventView(collection: shift_events, collection2: conf_events)

    render: =>
      @$el.fullCalendar
        header:
          left: 'today prev,next title'
          #                            center: 'title'
          right: 'month,agendaWeek' #basicWeek
        selectable: authorized
        #                          selectable: false
        selectHelper: true
        editable: authorized
        #                          editable: false
        ignoreTimezone: false
        select: @select
        eventClick: @eventClick
        eventDrop: @eventDropOrResize
        eventResize: @eventDropOrResize
        currentTimezone: 'America/New_York'
        allDayDefault: false
        allDayText: 'Shifts'
        weekMode: 'liquid'
        height: get_calendar_height()
        eventRender: (event, element) ->
          fcEventStartParsed = $.fullCalendar.parseDate(event.start)
          fcEventEndParsed = $.fullCalendar.parseDate(event.end)
          eventTimeF = []
          for dateTime in [fcEventStartParsed, fcEventEndParsed]
            if $.fullCalendar.formatDate(dateTime, "mm") > 0
              eventTimeF[_i] = $.fullCalendar.formatDate(dateTime, "h:mmt")
            else
              eventTimeF[_i] = $.fullCalendar.formatDate(dateTime, "ht")
          if event.shift
            event_variables =
            #                                'title': event.title
              'resident': event.resident
              'profile': false
              'first_name': false
              'last_name': false
              'shift_initials': shifts.get(event.shift).get('initials')
              'shift_abbr': shifts.get(event.shift).get('abbr')
              'shift_name': shifts.get(event.shift).get('name')
              'shift_cash': shifts.get(event.shift).get('cash')
              #                                'division': event.div
              #                                'url': event.link
              'start_time': eventTimeF[0]
              'end_time': eventTimeF[1]
              'id': event.id
            if event.user
              user_variables =
                'last_name': users.get(event.user).get('last_name')
                'first_name': users.get(event.user).get('first_name')
                'profile': users.get(event.user).get('profile')
              $.extend(event_variables, user_variables)
            event_template = _.template $("#shiftevent_template").html()
          else
            event_variables =
              'title': event.title
              'presenter': event.presenter
              'type': event.type
              'division': event.div
              'url': event.link
              'start_time': eventTimeF[0]
              'end_time': eventTimeF[1]
              'id': event.id
            event_template = _.template $("#confevent_template").html()
          compiled_event = event_template(event_variables)
          element.html(compiled_event)
          true

    addAll: =>
      booted = false
      bootstrapped_data = @$el.fullCalendar('clientEvents')
      if bootstrapped_data[0]
        booted = true

      @$el.fullCalendar 'removeEvents'
      @$el.fullCalendar 'addEventSource', @collection.filtered(@options.event_filter).toJSON()
      @$el.fullCalendar 'addEventSource', @options.collection2.filtered(@options.event_filter).toJSON()

    #                        if booted
    #                          @addPopup()

    addOne: (event) =>
      @$el.fullCalendar 'renderEvent', event.toJSON()

    #                      removeAll: =>
    #                        @$el.fullCalendar 'removeEventSource', @collection.toJSON()

    select: (startDate, endDate) =>
      # TODO: allow creation of call events?=
      @eventView.collection = @options.collection2
      @eventView.model = new ConfEvent
        start: startDate
        end: endDate
        date: startDate # for Django model (until I delete 'date' from Events abstract class)
      @eventView.render()

    eventClick: (fcEvent) =>
      if fcEvent.shift
        true
      else
        @eventView.model = @options.collection2.get fcEvent.resource_uri
        @eventView.render() unless authorized is false # might not be needed here

    change: (event)  =>
      # Look up the underlying event in the calendar and update its details from the model
      fcEvent = @$el.fullCalendar('clientEvents', event.get 'id')[0]
      #                        fcEvent = @$el.fullCalendar('clientEvents', (ev) -> if ev.id is event.get 'id')[0]
      fcEvent.title = event.get 'title'
      fcEvent.presenter = event.get 'presenter'
      fcEvent.div = event.get 'div'
      fcEvent.link = event.get 'link'
      fcEvent.conference = event.get 'conference'
      fcEvent.start = event.get 'start'
      fcEvent.end = event.get 'end'
      @$el.fullCalendar 'updateEvent', fcEvent

    eventDropOrResize: (fcEvent) =>
      # Lookup the model that has the ID of the event and update its attributes
      if fcEvent.conference
        @options.collection2.get(fcEvent.resource_uri).save start: fcEvent.start, end: fcEvent.end
      else
        @collection.get(fcEvent.resource_uri).save start: fcEvent.start, end: fcEvent.end

    destroy: (event) =>
      @$el.fullCalendar 'removeEvents', event.get 'id' #event.id

  class EventView extends Backbone.View
    render: =>
      if @model instanceof ConfEvent
        @setElement $('#confEventModal')
      if @model instanceof ShiftEvent
        @setElement $('#shiftEventModal')
      fcEventStartParsed = $.fullCalendar.parseDate(@model.get('start')) # set by table cell click for new Models
      fcEventEndParsed = $.fullCalendar.parseDate(@model.get('end')) # set by table cell click for new Models
      eventDateF = $.fullCalendar.formatDate(fcEventStartParsed, "MMMM dS yyyy")
      eventStartF = $.fullCalendar.formatDate(fcEventStartParsed, "HHmm")
      eventEndF = $.fullCalendar.formatDate(fcEventEndParsed, "HHmm")
      if @model.isNew()
        @$el.find('.btn-danger').hide()
      else
        @$el.find('.btn-danger').show()
      #                          title: (if @model.isNew() then 'New' else 'Edit') + ' Event'
      if eventStartF is '0000' and eventEndF is '0000' # creating a new event on month view
        true
      else
        $("#start_time").timepicker 'setTime', $.fullCalendar.formatDate(fcEventStartParsed, "HH:mm")
        $("#end_time").timepicker 'setTime', $.fullCalendar.formatDate(fcEventEndParsed, "HH:mm")
      if not @model.isNew()
        $("#type :radio[value='" + @model.get('conference') + "']").prop('checked', true)
      if @model instanceof ConfEvent
        @$el.find('h3').text 'Conference for ' + eventDateF
        $('#title').val @model.get('title')
        $('#presenter').val @model.get('presenter')
        $('#link').val @model.get('link')
        $('#division').val @model.get('div')
      if @model instanceof ShiftEvent
        true
      #                        $('#division').next().text @model.get('div') || 'None' # set text of Bootstrap generated <a class="btn">
      #                        select.find('.btn:eq(0)').text($(this).text());
      @$el.modal()

      @$el.find('.btn-primary').on 'click', @save
      @$el.find('.btn-close, .close').on 'click', @close
      $('.modal-backdrop').on 'click', @close
      @$el.find('.btn-danger').on 'click', @destroy
      @

    #                    $('#eventModal').on 'shown', () ->

    save: =>
      fcEventStartParsed = $.fullCalendar.parseDate @model.get('start')
      eventDateF = $.fullCalendar.formatDate(fcEventStartParsed, "yyyy-MM-dd")
      startTime = @$('#start_time').val()
      endTime = @$('#end_time').val()
      times = []
      for timePoint in [startTime, endTime]
        AMPM = timePoint.slice(-2)
        mins = timePoint.slice(-4, -2)
        hour = timePoint.slice(0, 2)
        hour = hour.replace(":", "")
        hour = (if hour.length > 1 then hour else "0" + hour)
        hour = hour % 12 + (if AMPM is "am" then 0 else 12)
        hour = (if hour < 10 then "0" + hour else hour)
        times[_i] = (hour+':'+mins)
      conference = @$("#type input[name='typeRadios']:checked").val()
      conference = if conference is 'null' then null else conference
      @model.set
      #                          'venue': @$("#venue input[name='venueRadios']:checked").val()
        'title': @$('#title').val()
        'presenter': @$('#presenter').val()
        'div': @$('#division').val()
        'link': @$('#link').val()
        'conference': conference
        'start': eventDateF + 'T' + times[0]
        'end': eventDateF + 'T' + times[1]

      if @model.isNew()
        @options.collection2.create @model, wait: true, success: @close
        # wait for the server response of full object with id before passing it on for rendering
      else
        @model.save {}, success: @close

    close: =>
      @$el.find('.btn-primary').off 'click', @save
      @$el.find('.btn-close, .close').off 'click', @close # needed?
      $('.modal-backdrop').off 'click', @close # needed?
      @$el.find('.btn-danger').off 'click', @destroy
      @$el.modal 'hide'

    destroy: =>
      @model.destroy wait:true, success: @close

  $('#confEventModal .time').timepicker()
  #                      'minTime': '7:00am'
  #                      'maxTime': '7:00pm'

  conferences = new Conferences
  conferences.reset JSON.parse(c_json)
  conferences.sort()
  #                    conferences.fetch()
  #                    # TODO: change
  noon = conferences.get('/api/v1/conference/1/')
  am = conferences.get('/api/v1/conference/2/')

  $("#start_time").timepicker 'setTime', am.get('start_time')
  $("#end_time").timepicker 'setTime', am.get('end_time')
  $('#confEventModal #typeRadios1').on 'click', () ->
    $("#start_time").timepicker 'setTime', noon.get('start_time')
    $("#start_time").timepicker
      'minTime': '12:00pm'
      'maxTime': '7:00pm'
    $("#end_time").timepicker 'setTime', noon.get('end_time')
    $("#end_time").timepicker
      'minTime': '12:00pm'
      'maxTime': '7:00pm'
  $('#confEventModal #typeRadios2').on 'click', () ->
    $("#start_time").timepicker 'setTime', am.get('start_time')
    $("#start_time").timepicker
      'minTime': '7:00am'
      'maxTime': '12:00pm'
    $("#end_time").timepicker 'setTime', am.get('end_time')
    $("#end_time").timepicker
      'minTime': '7:00am'
      'maxTime': '12:00pm'
  $('#confEventModal #typeRadios3').on 'click', () ->
    $("#start_time").timepicker
      'minTime': null
      'maxTime': null
    $("#end_time").timepicker
      'minTime': null
      'maxTime': null

  users = new Users
  users.reset JSON.parse(u_json)
  users.sort()
  #                    users.fetch()

  shifts = new Shifts
  shifts.reset JSON.parse(s_json)
  shifts.sort()

  event_filters = new EventFilters()
  event_filters.reset JSON.parse(ef_json)

  subspecialties = new Subspecialties()
  subspecialties.reset JSON.parse(sub_json)
  subspecialties.sort()

  shift_events = new ShiftEvents
  conf_events = new ConfEvents

  event_filter = event_filters.get('/api/v1/eventfilter/8/') # "current" event_filter

  new EventsView(el: $("#calendar"), collection: shift_events, collection2: conf_events, event_filter: event_filter).render()

  #                    $('#calendar').fullCalendar 'addEventSource', 'https://www.google.com/calendar/feeds/ecadjvmlkikvpm8hoa9262gh40%40group.calendar.google.com/public/basic'

  conf_on = true
  #                    conf_on = false
  if conf_on
    conf_events.reset JSON.parse(ce_json) # pass first month's data as a json object
  #                      conf_events.fetch
  #                        data:
  #                          'start__gte': '2012-06-01'

  shift_on = true
  #                    shift_on = false
  if shift_on
    shift_events.reset JSON.parse(se_json) # pass first month's data as a json object
#                      console.log se_json
#                      shift_events.fetch
#                        data:
#                          'start__gte': '2012-06-01'

  new EventFiltersView(el: $("#event-filters"), collection: event_filters, event_filter: event_filter).render()

  # For some reason need to use .fc-event as the selector, .shift-event doesn't work
  $('body').popover(
    selector: '.fc-event'
    title: () ->
      $('.shift-event', this).attr('title')
    content: ->
      $('.shift-event', this).attr('data-content')
    html: true
    'placement': (tip, element) -> # from https://github.com/twitter/bootstrap/issues/345#issuecomment-5972619
      isWithinBounds = (elementPosition) ->
        boundTop < elementPosition.top and boundLeft < elementPosition.left and boundRight > (elementPosition.left + actualWidth) and boundBottom > (elementPosition.top + actualHeight)
      $element = $(element)
      pos = $.extend({}, $element.offset(),
        width: element.offsetWidth
        height: element.offsetHeight
      )
      actualWidth = 283
      actualHeight = 117
      boundTop = $(document).scrollTop()
      boundLeft = $(document).scrollLeft()
      boundRight = boundLeft + $(window).width()
      boundBottom = boundTop + $(window).height()

      elementLeft =
        top: pos.top + pos.height / 2 - actualHeight / 2
        left: pos.left - actualWidth

      elementRight =
        top: pos.top + pos.height / 2 - actualHeight / 2
        left: pos.left + pos.width

      left = isWithinBounds(elementLeft)
      right = isWithinBounds(elementRight)
      (if right then "right" else (if left then "left" else "top"))
  )

  $(window).resize ->
    $('#calendar').fullCalendar 'option', 'height', get_calendar_height()


#                    $('.fc-event').tooltip
#                      title: 'hey'
#                    $('#calendar .fc-button').addClass 'btn'
#                    $('#calendar td > .fc-corner-left').each ->
#                      $(this).next('.fc-corner-right').andSelf().wrapAll '<div class="btn-group" />'
#                    $('#calendar .fc-header-left').wrapInner '<div class="btn-toolbar" />'

#                    $('#filter-controls .nav a').click (e) ->
#                      e.preventDefault()
#                      controls = $(this).attr('href')
#                      $(controls).toggle()
#                      $(this).parent().toggleClass('active')
#                      $('#conf-controls').toggle()
#                    $(".chzn-select").chosen()

#                    $('#calendar div[rel=tooltip], #calendar span[rel=tooltip]').tooltip()

#                    $('.event').hover ->
#                      $('.end').show() #
#                    , ->
#                      $('.end').hide() #.removeClass('display')

#                    $(".event").on "toggle", ".end", ->
#                      if not $(this).attr("data-toggled") or $(this).attr("data-toggled") is "off"
#                        $(this).attr "data-toggled", "on"
#                      else $(this).attr "data-toggled", "off"  if $(this).attr("data-toggled") is "on"
