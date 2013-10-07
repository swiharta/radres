jQuery(document).ready(function($) {
	// $('textarea').growfield();
	$('.edit').editable('{% url ajax_save %}', {
		indicator : 'Saving...',
		cancel    : 'Cancel',
		submit    : 'OK',
		tooltip   : 'Click to edit...'
	});
	$('.edit_area').editable('{% url ajax_save %}', { 
		type      : 'textarea',
		cancel    : 'Cancel',
		submit    : 'OK',
		indicator : '<img src="img/indicator.gif">',
		tooltip   : 'Click to edit...',
	});
	
	// CASE TAGS SELECT ------//
	
	$('#add_tags').click(function() {
		$('#tags_select').toggle('fast');
	});
	
	$("#tags_submit").submit(function(event){
		event.preventDefault(); // cancel the default action
		var form = $(this);
		var data = {
			case_id: {{ case.id }},
			tags: form.find('#id_tags').val(),
		};
		$.post("{% url add_tags %}", data, function(responseData) {
			if (responseData != "failure") {
				$('#tags_select').hide('slow');
				$('#add_tags_ok').fadeIn().delay(1200).fadeOut('slow');
			} else {
				alert("Failed to save.");
			}
		});
	});
	
	function choice_save() {
		// event.preventDefault(); // cancel the default action, superfluous?
		var choice = $(this).parent(); // targets <li> holding the form
		var data = {
			case_id: {{ case.id }},
			tag: choice.find('#id_tag').val(),
			text: choice.find('#id_text').val(),
			type : choice.find('#id_type').val(),
			id: choice.attr("id"),
		};
		$.post("{% url add_tag %}", data, function(result) {
			if (result != "failure") {
				choice.before($("li", result).get(0));
				choice.remove();
				$("#choices .choice_edit").click(choice_edit);
				$('.edit_area').editable('{% url ajax_save %}', { 
					type      : 'textarea',
					cancel    : 'Cancel',
					submit    : 'OK',
					indicator : '<img src="img/indicator.gif">',
					tooltip   : 'Click to edit...',
				});
			} else {
				alert("Failed to save.");
			}
		});
		return false;
	}
	
	function cancel_choice_edit() {
		var choice = $(this).parent().parent();
		var id = choice.attr("id");
		if (!id) { // if cancelling a new choice form
			choice.before('<li><a href="#" class="choice_edit">Add Choice</a></li>');
			choice.remove();
			$("#choices .choice_edit").click(choice_edit);
		}
		else {
		$.get("/cases/choice/" + id, null, function (result) {
			choice.before($("li", result).get(0));
			choice.remove();
			$("#choices .choice_edit").click(choice_edit);
			$('.edit_area').editable('{% url ajax_save %}', { 
				type      : 'textarea',
				cancel    : 'Cancel',
				submit    : 'OK',
				indicator : '<img src="img/indicator.gif">',
				tooltip   : 'Click to edit...',
			});
		});
		}
	}
	
	function choice_edit() {
		if ($('#tag_submit').length) { return false } // prevent editing multiple choices
		else {
		var choice = $(this).parent();
		var data = { id: choice.attr("id"), case_id: {{ case.id }} };
		$.get("{% url add_tag %}", data, function (result) {
			choice.html(result);
			$("#tag_submit").submit(choice_save);
			$("#cancel_choice_edit").click(cancel_choice_edit);
			//$("#tag_select").click(tag_select); // need to find a way to call autocomplete
			
			// SET TAG SELECT FILTERS
			
			$("#id_tag_text").autocomplete('/ajax_select/ajax_lookup/tags-select', {
				width: 320,
				formatItem: function(row) { return row[2]; },
				formatResult: function(row) { return row[1]; },
				dataType: "text",
				cacheLength: 1,
				extraParams: {	sub: function() { return $('#sub_select_tag').val(); },		
								peds: function() {	return $('#peds_checkbox_tag').is(':checked'); },
							 }
			});
			
			function receiveResult(event, data) {
				prev = $("#id_tag").val();
				if(prev) {
					kill_{{ func_slug }}(prev);
				}
				$("#id_tag").val(data[0]);
				$("#id_tag_text").val("");
				addKiller_{{ func_slug }}(data[1],data[0]);
				$("#id_tag_on_deck").trigger("added");
			}
			$("#id_tag_text").result(receiveResult);
			function addKiller_{{func_slug}}(repr,id) {
				kill = "<span class='iconic' id='kill_id_tag'>X</span>	";
				if(repr){
					$( "#id_tag_on_deck" ).empty();
					$( "#id_tag_on_deck" ).append( "<div>" + kill + repr + "</div>");
				} else {
					$( "#id_tag_on_deck > div" ).prepend(kill);
				}
				$("#kill_id_tag").click(function() { return function(){
					kill_{{func_slug}}();
					$("#id_tag_on_deck").trigger("killed");
				}}() );
			}
			function kill_{{func_slug}}() {
				$("#id_tag").val( '' );
				$( "#id_tag_on_deck" ).children().fadeOut(1.0).remove();
			}
			if($("#id_tag").val()) { // add X for initial value if any
				addKiller_{{ func_slug }}(null,$("#id_tag").val());
			}
			$("#id_tag").bind('didAddPopup',function(event,id,repr) {
				data = Array();
				data[0] = id;
				data[1] = repr;
				receiveResult(null,data);
			});
		
		
			$("#sub_select_tag").val( {{ case.subspecialty.id }} );
			{% if case.pediatric %}
			$("#peds_checkbox_tag").attr('checked', true);
			{% else %}
			$("#peds_checkbox_tag").attr('checked', false);
			{% endif %}
		}, 'html');
		return false;
	}}
	
	$("#choices .choice_edit").click(choice_edit);
	
	// SET TAGS SELECT FILTERS
	
	sub = {{ case.subspecialty.id }}//$('#id_subspecialty').val();	
	$("#sub_select").val(sub);
	
	$("#id_subspecialty").change( function(event) {
		sub = $('#id_subspecialty').val();
		$("#sub_select").val(sub);
	});	
	
	{% if case.pediatric %}
	$("#peds_checkbox").attr('checked', true);
	{% endif %}
	
	$("#id_pediatric").change( function(event) {	
		if ($('#id_pediatric').is(':checked')) 
			{ $("#peds_checkbox").attr('checked', true); } 
		else 
			{ $("#peds_checkbox").attr('checked', false); } 
	 });
});