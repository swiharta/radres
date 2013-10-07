$(document).ready ->

                    get_calendar_height = ->
                      $(window).height() - 80

                    class Conference extends Backbone.Model
#                      idAttribute: 'resource_uri'

                    class Conferences extends Backbone.Collection
                      model: Conference
                      url: '/api/v1/conference/?format=json'

                    class Event extends Backbone.Model

                    class Events extends Backbone.Collection
                      model: Event
#                      url: '/api/v1/shiftevent/?format=json'
                      url: '/api/v1/confevent/?format=json'

                    class EventsView extends Backbone.View
                      initialize: ->
                        @collection.bind 'reset', @addAll
                        @collection.bind 'add', @addOne
                        @collection.bind 'change', @change
                        @collection.bind 'destroy', @destroy
                        @eventView = new EventView

                      render: =>
                        @$el.fullCalendar
                          header:
                            left: 'today prev,next title'
#                            center: 'title'
                            right: 'month,agendaWeek' #basicWeek
                          buttonText:
                            prev: ' ◄ '
                            next: ' ► '
                          selectable: authorized
                          selectHelper: true
                          editable: authorized
                          ignoreTimezone: false
                          select: @select
                          eventClick: @eventClick
                          eventDrop: @eventDropOrResize
                          eventResize: @eventDropOrResize
                          currentTimezone: 'America/New_York'
                          allDayDefault: false
                          height: get_calendar_height()
                          weekMode: 'liquid'
                          eventRender: (event, element) ->
                            fcEventStartParsed = $.fullCalendar.parseDate(event.start)
                            fcEventEndParsed = $.fullCalendar.parseDate(event.end)
                            eventTimeF = []
                            for dateTime in [fcEventStartParsed, fcEventEndParsed]
                              if $.fullCalendar.formatDate(dateTime, "mm") > 0
                                eventTimeF[_i] = $.fullCalendar.formatDate(dateTime, "h:mmt")
                              else
                                eventTimeF[_i] = $.fullCalendar.formatDate(dateTime, "ht")
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
#                            event_variables =
#                              'name': event.title
#                              'shift__initials': event.shift__initials
#                              'shift__name': event.shift__name
#                              'shift__cash': event.shift__cash
#                              'shift__start': event.shift__start
#                              'shift__end': event.shift__end
#                            event_template = _.template $("#shiftevent_template").html()
                            compiled_event = event_template(event_variables)
                            element.html(compiled_event)
                            true

                      addAll: =>
                        @$el.fullCalendar 'removeEvents'
                        @$el.fullCalendar 'addEventSource', @collection.toJSON()

                      addOne: (event) =>
                        @$el.fullCalendar 'renderEvent', event.toJSON()

#                      removeAll: =>
#                        @$el.fullCalendar 'removeEventSource', @collection.toJSON()

                      select: (startDate, endDate) =>
                        @eventView.collection = @collection
                        @eventView.model = new Event
                          start: startDate
                          end: endDate
                          date: startDate # for Django model (until I delete 'date' from Events abstract class)
                        @eventView.render()

                      eventClick: (fcEvent) =>
                        @eventView.model = @collection.get fcEvent.resource_uri
                        @eventView.render() unless authorized is false # might not be needed here

                      change: (event)  =>
                      # Look up the underlying event in the calendar and update its details from the model
                        fcEvent = @$el.fullCalendar('clientEvents', event.get 'id')[0]
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
                        @collection.get(fcEvent.resource_uri).save start: fcEvent.start, end: fcEvent.end

                      destroy: (event) =>
                        @$el.fullCalendar 'removeEvents', event.get 'id' #event.id

                    class EventView extends Backbone.View
                      el: $('#eventModal')

                      render: => # TODO: don't take start and end from new event on month view (midnight)
                        fcEventStartParsed = $.fullCalendar.parseDate(@model.get('start')) # set by table cell click for new Models
                        fcEventEndParsed = $.fullCalendar.parseDate(@model.get('end')) # set by table cell click for new Models
                        eventDateF = $.fullCalendar.formatDate(fcEventStartParsed, "MMMM dS yyyy")
                        eventStartF = $.fullCalendar.formatDate(fcEventStartParsed, "HHmm")
                        eventEndF = $.fullCalendar.formatDate(fcEventEndParsed, "HHmm")
                        @$el.find('h3').text 'Conference for ' + eventDateF
                        if @model.isNew()
                          @$el.find('.btn-danger').hide()
                        else
                          @$el.find('.btn-danger').show()
                          $("#type :radio[value='" + @model.get('conference') + "']").prop('checked', true)
                        if eventStartF is '0000' and eventEndF is '0000'
                          true
                        else
                          $("#start_time").timepicker 'setTime', $.fullCalendar.formatDate(fcEventStartParsed, "HH:mm")
                          $("#end_time").timepicker 'setTime', $.fullCalendar.formatDate(fcEventEndParsed, "HH:mm")
                        $('#title').val @model.get('title')
                        $('#presenter').val @model.get('presenter')
                        $('#link').val @model.get('link')
                        $('#division').val @model.get('div')
                        @$el.modal()

                        @$el.find('.btn-primary').on 'click', @save
                        @$el.find('.btn-close, .close').on 'click', @close
                        $('.modal-backdrop').on 'click', @close
                        @$el.find('.btn-danger').on 'click', @destroy
                        @

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
                          @collection.create @model, wait: true, success: @close
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

                    $('#eventModal .time').timepicker
                      'minTime': '7:00am'
                      'maxTime': '7:00pm'

                    conferences = new Conferences
                    conferences.reset JSON.parse(c_json)
                    noon = conferences.get('/api/v1/conference/1/')
                    am = conferences.get('/api/v1/conference/2/')

                    $("#start_time").timepicker 'setTime', am.get('start_time')
                    $("#end_time").timepicker 'setTime', am.get('end_time')
                    $('#eventModal #typeRadios1').on 'click', () ->
                      $("#start_time").timepicker 'setTime', noon.get('start_time')
                      $("#start_time").timepicker
                        'minTime': '12:00pm'
                        'maxTime': '7:00pm'
                      $("#end_time").timepicker 'setTime', noon.get('end_time')
                      $("#end_time").timepicker
                        'minTime': '12:00pm'
                        'maxTime': '7:00pm'
                    $('#eventModal #typeRadios2').on 'click', () ->
                      $("#start_time").timepicker 'setTime', am.get('start_time')
                      $("#start_time").timepicker
                        'minTime': '7:00am'
                        'maxTime': '12:00pm'
                      $("#end_time").timepicker 'setTime', am.get('end_time')
                      $("#end_time").timepicker
                        'minTime': '7:00am'
                        'maxTime': '12:00pm'
                    $('#eventModal #typeRadios3').on 'click', () ->
                      $("#start_time").timepicker
                        'minTime': null
                        'maxTime': null
                      $("#end_time").timepicker
                        'minTime': null
                        'maxTime': null
                        
                    events = new Events

                    new EventsView(el: $("#calendar"), collection: events).render()

                    events.reset JSON.parse(ce_json) # pass first month's data as a json object
                    events.fetch()

                    $(window).resize ->
                      $('#calendar').fullCalendar 'option', 'height', get_calendar_height()
#                      data:
#                        'start__gte': '2011-01-01'
#                        'conference': "/api/v1/conference/2/"
